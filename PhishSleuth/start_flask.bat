@echo off
cd /d "%~dp0phish-api"
start /min cmd /c python app.py
cd /d "%~dp0sms-email-spam-classifier-main"
start /min cmd /c python -m streamlit run --server.headless true app.py
