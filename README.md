# FloodGuard AI — AI-Based Flood Risk Prediction & Early Warning System

This repository contains the Streamlit implementation of **FloodGuard AI** for the CAT-03 Real-Time Case Study using an AI-Enabled Cloud Tool.

## Files Included
- `app.py`: Streamlit application with the 9 flood-risk input criteria, preset scenarios, form submission state control (keeps results unchanged while editing until **Analyze Flood Risk** is clicked), risk scoring engine, 72-hour trend view, and case study tab.
- `requirements.txt`: Python dependencies for Streamlit.

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, and `README.md` to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub, select your repository, set **Main file path** to `app.py`, and click **Deploy**.
