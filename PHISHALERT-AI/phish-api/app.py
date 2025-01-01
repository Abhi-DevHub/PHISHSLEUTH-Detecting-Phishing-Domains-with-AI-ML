import numpy as np
from flask import Flask, request, jsonify
import pickle
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
import whois
import tldextract
import re
import string
import datetime
from dateutil.relativedelta import relativedelta
from csv import reader
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
model = pickle.load(open('SVM_Model.pkl', 'rb'))

# Function to check for IP address in URL
def having_ip(url):
    split_url = urlparse(url).netloc.replace(".", "")
    counter_hex = sum(1 for i in split_url if i in string.hexdigits)
    return 1 if counter_hex >= len(split_url) else 0

# Function to check the presence of '@' in URL
def have_at_sign(url):
    return 1 if any(char in url for char in ['@', '~', '`', '!', '$', '%', '&']) else 0

# Function to find the length of URL
def get_length(url):
    return 1 if len(url) >= 54 else 0

# Function to count the number of '/' in URL
def get_depth(url):
    return len(urlparse(url).path.split('/'))

# Function to check for redirection '//'
def redirection(url):
    return 1 if url.rfind('//') > 6 and url.rfind('//') > 7 else 0

# Function to check for "HTTPS" token in the domain part of the URL
def http_domain(url):
    return 1 if 'https' in urlparse(url).netloc else 0

# Function to check for shortening services in URL
def tiny_url(url):
    shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|" \
                          r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|" \
                          r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|" \
                          r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|" \
                          r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|" \
                          r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|" \
                          r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|" \
                          r"tr\.im|link\.zip\.net"
    return 1 if re.search(shortening_services, url) else 0

# Function to check for prefix or suffix separated by '-' in the domain
def prefix_suffix(url):
    return 1 if '-' in urlparse(url).netloc else 0

# Function to check web traffic
def web_traffic(url):
    try:
        extract_res = tldextract.extract(url)
        url_ref = extract_res.domain + "." + extract_res.suffix
        html_content = requests.get(f"https://www.alexa.com/siteinfo/{url_ref}").text
        value = int(BeautifulSoup(html_content, "lxml").find('div', {'class': "rankmini-rank"}).text.replace(",", ""))
        return 0 if value < 100000 else 1
    except:
        return 1

# Function to check the survival time of the domain
def domain_age(url):
    try:
        whois_res = whois.whois(url)
        return 0 if datetime.datetime.now() > whois_res["creation_date"][0] + relativedelta(months=+6) else 1
    except:
        return 1

# Function to check the end time of the domain
def domain_end(domain_name):
    expiration_date = domain_name.expiration_date
    if isinstance(expiration_date, str):
        try:
            expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")
        except:
            return 1
    if expiration_date is None:
        return 1
    elif type(expiration_date) is list:
        today = datetime.datetime.now()
        domain_date = abs((expiration_date[0] - today).days)
        return 1 if (domain_date / 30) < 6 else 0
    else:
        today = datetime.datetime.now()
        domain_date = abs((expiration_date - today).days)
        return 1 if (domain_date / 30) < 6 else 0

# Function to check for iframe redirection
def iframe(response):
    return 1 if response == "" or re.findall(r"[<iframe>|<frameBorder>]", response.text) else 0

# Function to check the effect of mouse over on the status bar
def mouse_over(response):
    return 1 if response == "" or re.findall("<script>.+onmouseover.+</script>", response.text) else 0

# Function to check the number of forwardings
def forwarding(response):
    return 1 if response == "" or len(response.history) <= 2 else 0

# Function to check if the URL exists in popular websites data
def check_csv(url):
    try:
        check_url = urlparse(url).netloc
    except:
        return 1
    with open('Web_Scrapped_websites.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        return 0 if any(row[0] == check_url for row in csv_reader) else 1

# Function for feature extraction
def feature_extraction(url):
    features = [
        having_ip(url),
        have_at_sign(url),
        get_length(url),
        get_depth(url),
        redirection(url),
        http_domain(url),
        tiny_url(url),
        prefix_suffix(url),
    ]

    # Domain based features
    dns = 0
    try:
        domain_name = whois.whois(urlparse(url).netloc)
    except:
        dns = 1

    features.extend([
        dns,
        web_traffic(url),
        domain_age(url) if dns == 0 else 1,
        domain_end(domain_name) if dns == 0 else 1,
    ])

    # HTML & Javascript based features
    try:
        response = requests.get(url)
    except:
        response = ""

    features.extend([
        iframe(response),
        mouse_over(response),
        forwarding(response),
    ])

    return features

# Flask routes
@app.route('/', methods=["GET", "POST"])
def home():
    return "Hello World"

@app.route('/post', methods=['POST'])
def predict():
    url = request.form['URL']
    data_phish = check_csv(url)
    if data_phish == 0:
        return "0"
    else:
        features = feature_extraction(url)
        if features.count(0) == 15 or features.count(0) == 14:
            prediction = 0
        else:
            prediction = model.predict([features])[0]
        return "-1" if prediction == 1 and data_phish == 1 else "1"

if __name__ == "__main__":
    app.run(debug=True)