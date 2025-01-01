import streamlit as st
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.pipeline import Pipeline
import joblib
from scipy.sparse import csr_matrix
import nltk

# Download NLTK data if not already downloaded
nltk.download('stopwords')
nltk.download('punkt')

ps = PorterStemmer()

def transform_text(text):
    text = text.lower()
    text_tokens = word_tokenize(text)

    # Remove non-alphanumeric characters
    text_tokens = [token for token in text_tokens if token.isalnum()]

    # Remove stopwords and punctuation, and apply stemming
    processed_tokens = [ps.stem(token) for token in text_tokens if token not in stopwords.words('english') and token not in string.punctuation]

    return " ".join(processed_tokens)

# Load existing model and vectorizer using joblib
vectorizer = joblib.load('vectorizer.pkl')
model = joblib.load('model.pkl')

# Create a pipeline with the vectorizer and model
pipeline = Pipeline([('vectorizer', vectorizer), ('model', model)])

st.title("Email/SMS Spam Classifier")

input_sms = st.text_area("Enter the message")

if st.button('Predict'):
    # Preprocess the input message
    transformed_sms = transform_text(input_sms)
    # Predict the class
    result = pipeline.predict([transformed_sms])[0]
    # Display the prediction
    if result == 1:
        st.header("Spam")
    else:
        st.header("Not Spam")
