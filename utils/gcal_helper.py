import datetime
import google.oauth2.credentials
from googleapiclient.discovery import build
from database import get_user_data

# Hardcoded for Hackathon (You can change this later)
CLIENT_ID = "YOUR_CLIENT_ID_FROM_JSON" 
CLIENT_SECRET = "YOUR_CLIENT_SECRET_FROM_JSON"
# NOTE: In a real app, load these from os.getenv()! 
# For now, if you are stuck, you can paste the strings here or use os.getenv.

def get_google_creds(user_id):
    """
    Reconstructs the Google Credentials object from our Database.
    """
    user = get_user_data(user_id)
    if not user:
        return None
    
    # We load the "keys" from the database
    creds = google.oauth2.credentials.Credentials(
        token=None,  # Access token is temporary, we let Google refresh it
        refresh_token=user['refresh_token'],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"), # Make sure to add this to Render!
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"), # Make sure to add this to Render!
        scopes=['https://www.googleapis.com/auth/calendar.events']
    )
    return creds

def check_busy_times(user_ids, start_time_iso, end_time_iso):
    """
    Checks the calendars of multiple users.
    Returns a list of 'busy' blocks.
    """
    service_list = []
    
    # 1. Build a Service for EACH user
    # We need to act as each person to see their "primary" calendar
    for uid in user_ids:
        creds = get_google_creds(uid)
        if creds:
            try:
                service = build('calendar', 'v3', credentials=creds)
                service_list.append({"id": uid, "service": service})
            except Exception as e:
                print(f"❌ Could not auth user {uid}: {e}")

    if not service_list:
        return {"error": "No valid users found"}

    # 2. Ask Google for Free/Busy data
    busy_intervals = []
    
    for item in service_list:
        try:
            body = {
                "timeMin": start_time_iso, # e.g., "2024-02-12T09:00:00Z"
                "timeMax": end_time_iso,
                "items": [{"id": "primary"}]
            }
            events_result = item['service'].freebusy().query(body=body).execute()
            
            # Extract the busy chunks
            calendars = events_result.get('calendars', {})
            primary = calendars.get('primary', {})
            busy = primary.get('busy', [])
            
            # Add to our master list
            # We tag it with the user ID so we know WHO is busy
            for block in busy:
                busy_intervals.append({
                    "user": item['id'],
                    "start": block['start'],
                    "end": block['end']
                })
                
        except Exception as e:
            print(f"❌ Error checking calendar for {item['id']}: {e}")

    return busy_intervals