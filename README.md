# 📅 GCal-Bridge: Private Shared Calendar UI

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.47%2B-ff69b4.svg)](https://streamlit.io)
[![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat&logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Google Calendar](https://img.shields.io/badge/Google_Calendar-4285F4?style=flat&logo=google-calendar&logoColor=white)](https://developers.google.com/calendar)
[![Security: Token Auth](https://img.shields.io/badge/Security-URL_Token-green.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A custom web interface built with **Streamlit** that allows a private group to view and edit a Google Calendar without requiring individual Google accounts.

## 🛠️ Tech Stack
- **Backend:** Python
- **Frontend:** Streamlit
- **API:** Google Calendar API (v3)
- **Auth:** Google Service Account & Custom URL-token security
- **Deployment:** Streamlit Cloud

## 💡 The Problem
Google Calendar typically requires users to have a Google account to edit events. For non-tech-savvy users or groups without Google accounts, this creates a barrier. 

## 🚀 The Solution
This app acts as a secure proxy. Using a **Google Service Account**, the app interacts with the Calendar API on behalf of the users. 
- **Privacy:** Access is restricted via a unique URL access token.
- **Simplicity:** No login/password required for the end-user.
- **Zero Friction:** One-click access to add or view events.

## 📸 Demo
> Note: For privacy reasons, the live demo is restricted to authorized users.

## ⚙️ Setup & Architecture
1. **Google Cloud Console:** Enable Calendar API and create a Service Account.
2. **Calendar Permissions:** Share the target calendar with the Service Account's email.
3. **Secrets Management:** The app uses Streamlit's `secrets.toml` to store:
    - Google JSON credentials.
    - The target Calendar ID.
    - A custom `access_key` for URL-based authentication.

## 🔒 Security Features
- **No Data Storage:** The app doesn't store events; it fetches them in real-time from Google.
- **Tokenized Access:** Access is only granted if a specific `?key=...` parameter is present in the URL.
- **Environment Variables:** All sensitive keys are handled through encrypted secrets.
