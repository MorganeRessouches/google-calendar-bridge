import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# --- CONFIGURATION ---
creds_dict = st.secrets["gcp_service_account"]
CALENDAR_ID = st.secrets["calendar_id"]
CALENDAR_NAME = st.secrets["calendar_name"]
VALID_KEY = st.secrets["access_key"]

# Check access_key
query_params = st.query_params
user_key = query_params.get("key")

if user_key != VALID_KEY:
    st.error("🔒 Access Denied. Please use the private link provided.")
    st.stop()

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

service = get_calendar_service()

st.title(f"📅 {CALENDAR_NAME}")

# --- ADD AN EVENT ---
with st.form("Ajouter un événement"):
    summary = st.text_input("Nom de l'événement")
    date = st.date_input("Date")
    submit = st.form_submit_button("Ajouter")

    if submit:
        # Date format for Google API (ISO format)
        start_time = datetime.combine(date, datetime.min.time()).isoformat() + 'Z'
        end_time = datetime.combine(date, datetime.max.time()).isoformat() + 'Z'
        
        event = {
            'summary': summary,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
        }
        
        service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        st.success(f"Événement '{summary}' ajouté !")

# --- DISPLAY EVENTS ---
st.subheader("Événements à venir")
now = datetime.now().isoformat() + 'Z'
events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                      maxResults=10, singleEvents=True,
                                      orderBy='startTime').execute()
events = events_result.get('items', [])

if not events:
    st.write("Aucun événement trouvé.")
for event in events:
    start = event['start'].get('dateTime', event['start'].get('date'))
    st.write(f"• {start} : {event['summary']}")