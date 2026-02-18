import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, time
from streamlit_calendar import calendar
from babel.dates import format_date

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

# --- FUNCTIONS ---

def get_calendar_service():
    creds = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

def date_format(date):
    format_date(date, format='d MMMM', locale='fr_FR')

service = get_calendar_service()

# --- UI ---
st.set_page_config(
    page_title="Calendar",
    page_icon="📅",
    layout="wide"
)

st.title(f"📅 {CALENDAR_NAME}")

# --- ADD AN EVENT ---
with st.form("Ajouter un événement"):
    summary = st.text_input("Nom")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Date de début", datetime.now())
    with col2:
        end_date = st.date_input("Date de fin")

    submit = st.form_submit_button("Ajouter l'événement", use_container_width=True, type="primary")

    if submit:
        if not summary:
            st.error("Veuillez donner un nom à l'événement.")
        elif end_date < start_date:
            st.error("La date de fin ne peut pas être avant la date de début.")
        else:
            google_end_date = end_date + timedelta(days=1)
            
            event_body = {
                'summary': summary,
                'start': {'date': start_date.isoformat()},
                'end': {'date': google_end_date.isoformat()},
            }

            try:
                service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()
                st.success(f"✅ Événement '{summary}' ajouté avec succès !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de l'ajout : {e}")

# --- DISPLAY EVENTS ---
now = datetime.now().isoformat() + 'Z'
events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                      maxResults=10, singleEvents=True,
                                      orderBy='startTime').execute()
events = events_result.get('items', [])

processed_events = []
for event in events:
    is_all_day = 'date' in event['start']
    if is_all_day:
        dt_start = datetime.fromisoformat(event['start']['date'])
        # Remove 1 day for display
        dt_end = datetime.fromisoformat(event['end']['date']) - timedelta(days=1)
    else:
        dt_start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
        dt_end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
        
    processed_events.append({
        "title": event.get("summary", "Sans titre"),
        "start": dt_start,
        "end": dt_end,
        "id": event["id"],
        "is_all_day": is_all_day,
        "calendar_format": {
            "title": event.get("summary", "Sans titre"),
            "start": event['start'].get('dateTime', event['start'].get('date')),
            "end": event['end'].get('dateTime', event['end'].get('date')),
            "id": event["id"],
            "color": "#3788d8",
        }
    })

display_choice = st.segmented_control("Affichage", ["Liste", "Calendrier"], default="Liste", label_visibility="collapsed")

calendar_options = {
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "dayGridMonth", 
    "selectable": True,
    "editable": True,
    "firstDay": 1,
    "locale": "fr",
}

if display_choice == "Liste":
    st.subheader("📋 Récapitulatif des événements")
    
    if not events:
        st.write("Aucun événement prévu.")
    else:
        for e in processed_events:
            with st.container(border=True):
                col1, col2 = st.columns([1, 3])
                
                # Colonne 1 : La Date (Badge)
                with col1:
                    if e['is_all_day'] and e['start'].date() == e['end'].date():
                        # Un seul jour complet
                        st.markdown(f"**{format_date(e['start'], format='d MMMM', locale='fr_FR')}**")
                    else:
                        # Plage de dates
                        st.markdown(f"**{format_date(e['start'], format='d MMM', locale='fr_FR')}** - **{format_date(e['end'], format='d MMM', locale='fr_FR')}**")
                
                # Colonne 2 : Les Détails
                with col2:
                    st.markdown(f"**{e['title']}**")
                    
                    if e['is_all_day']:
                        if e['start'].date() == e['end'].date():
                            st.caption("Toute la journée")
                        else:
                            st.caption(f"Du {format_date(e['start'], format='full', locale='fr_FR')} au {format_date(e['end'], format='full', locale='fr_FR')}")
                    else:
                        # Événement avec horaires
                        if e['start'].date() == e['end'].date():
                            st.caption(f"{e['start'].strftime('%H:%M')} à {e['end'].strftime('%H:%M')}")
                        else:
                            st.caption(f"Du {e['start'].strftime('%d/%m %H:%M')} au {e['end'].strftime('%d/%m %H:%M')}")

else:
    # Affichage du calendrier (on extrait les formats calendar_format préparés plus haut)
    calendar_events = [e['calendar_format'] for e in processed_events]
    
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay",
        },
        "initialView": "dayGridMonth", 
        "selectable": True,
        "firstDay": 1,
        "locale": "fr",
    }
    
    calendar(events=calendar_events, options=calendar_options, key="cal-grid")