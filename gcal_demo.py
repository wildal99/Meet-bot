# gcal_demo.py


from __future__ import annotations
from datetime import datetime
from typing import List, Dict


import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build




# We only need read access to calendars / freebusy
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]




def get_gcal_credentials() -> Credentials:
   """
   Handles the OAuth dance:
   - Uses credentials.json (downloaded from Google Cloud)
   - Stores a token.json so you don't have to log in every time
   """
   creds: Credentials | None = None


   try:
       creds = Credentials.from_authorized_user_file("token.json", SCOPES)
   except Exception:
       creds = None


   if not creds or not creds.valid:
       if creds and creds.expired and creds.refresh_token:
           creds.refresh(Request())
       else:
           flow = InstalledAppFlow.from_client_secrets_file(
               "credentials.json", SCOPES
           )
           creds = flow.run_local_server(port=0)  # opens browser to log in


       # Save the credentials for next time
       with open("token.json", "w") as token:
           token.write(creds.to_json())


   return creds




def fetch_busy_from_gcal(
   start_iso: str,
   end_iso: str,
   timezone: str = "America/Toronto",
   calendar_id: str = "primary",
) -> List[Dict[str, str]]:
   """
   Uses the Google Calendar FreeBusy API to get busy intervals
   between start_iso and end_iso (both ISO strings).
   Returns a list of { "start": "...", "end": "..." } in ISO format
   compatible with your BusyInterval type.
   """
   creds = get_gcal_credentials()
   service = build("calendar", "v3", credentials=creds)


   body = {
       "timeMin": start_iso,
       "timeMax": end_iso,
       "timeZone": timezone,
       "items": [{"id": calendar_id}],
   }


   resp = service.freebusy().query(body=body).execute()


   busy_raw = resp["calendars"][calendar_id]["busy"]
   busy_intervals: List[Dict[str, str]] = []


   # busy_raw items look like { "start": "...", "end": "..." }
   for slot in busy_raw:
       start = slot["start"]  # e.g. "2026-02-03T14:00:00-05:00"
       end = slot["end"]


       # Optionally normalize microseconds, but usually not needed
       # We'll just strip them if present.
       start_clean = start.split(".")[0]
       end_clean = end.split(".")[0]


       busy_intervals.append(
           {
               "start": start_clean,
               "end": end_clean,
           }
       )


   return busy_intervals




if __name__ == "__main__":
   # Example range: the week you showed in the screenshot
   tz = "America/Toronto"
   start_iso = "2026-02-02T00:00:00-05:00"
   end_iso = "2026-02-08T23:59:59-05:00"


   busy = fetch_busy_from_gcal(start_iso, end_iso, timezone=tz)
   from pprint import pprint


   print("Busy intervals from Google Calendar:")
   pprint(busy)


