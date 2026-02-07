# main.py
from pprint import pprint
from scheduler import generate_meeting_options, MeetingRequest
from gcal_demo import fetch_busy_from_gcal




if __name__ == "__main__":
   # 1) Get my busy times from Google Calendar
   timezone = "America/Toronto"
   start_iso = "2026-02-02T00:00:00-05:00"
   end_iso = "2026-02-08T23:59:59-05:00"


   seun_busy = fetch_busy_from_gcal(start_iso, end_iso, timezone=timezone)


   # 2) Build the MeetingRequest using your new potential_time_blocks structure
   request: MeetingRequest = {
       "title": "Project Sync",
       "duration_minutes": 60,
       "timezone": timezone,
       "participant_ids": ["seun"],  # just you for now; later "seun", "tito", "deji"
       "potential_time_blocks": [
           {
               "start_date": "2026-02-02",
               "end_date": "2026-02-08",
               "start_time": "17:00",
               "end_time": "22:00",
           }
       ],
   }


   user_calendars = {
       "seun": seun_busy,
   }


   options = generate_meeting_options(request, user_calendars, max_options=5)
   pprint(options)