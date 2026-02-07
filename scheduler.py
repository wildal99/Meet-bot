# scheduler.py
from __future__ import annotations
from datetime import datetime, date, time, timedelta
from typing import Dict, List, TypedDict




# ---- Types ----


class TimeBlock(TypedDict):
   """
   A time block in which the meeting can occur.


   All fields must be normalized BEFORE reaching the scheduler:
   - start_date / end_date: "YYYY-MM-DD"
   - start_time / end_time: "HH:MM" in 24-hour format
   """
   start_date: str
   end_date: str
   start_time: str
   end_time: str




class MeetingRequest(TypedDict):
   """
   Parsed scheduling request coming from the AI layer.
   """
   title: str
   duration_minutes: int
   timezone: str
   participant_ids: List[str]
   potential_time_blocks: List[TimeBlock]




class BusyInterval(TypedDict):
   start: str   # "YYYY-MM-DDTHH:MM:SS"
   end: str     # "YYYY-MM-DDTHH:MM:SS"




class MeetTimeOption(TypedDict):
   start: str
   end: str
   free_participants: List[str]
   busy_participants: List[str]
   free_count: int
   score: float




# ---- Helpers ----


def parse_iso_datetime(dt_str: str) -> datetime:
   """Parse ISO datetime string."""
   return datetime.fromisoformat(dt_str)




def build_datetime(d: date, t: time) -> datetime:
   return datetime.combine(d, t)




def overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
   """Return True if [a_start, a_end) overlaps [b_start, b_end)."""
   return a_start < b_end and a_end > b_start




# ---- Core scheduler ----


def generate_meeting_options(
   request: MeetingRequest,
   user_calendars: Dict[str, List[BusyInterval]],
   max_options: int = 5,
   slot_step_minutes: int | None = None,
) -> List[MeetTimeOption]:
   """
   Given a meeting request + users' busy intervals, return best meeting time options.


   - Start times are aligned to a grid defined by slot_step_minutes (default 30).
   - Meeting duration can be any number of minutes.
   """
   duration = timedelta(minutes=request["duration_minutes"])


   # 🔹 Default grid = 30 minutes
   if slot_step_minutes is None:
       slot_step_minutes = 30
   slot_step = timedelta(minutes=slot_step_minutes)


   participant_ids = request["participant_ids"]


   # 1) Normalize busy intervals
   normalized_busy: Dict[str, List[tuple[datetime, datetime]]] = {}
   for user_id in participant_ids:
       intervals: List[tuple[datetime, datetime]] = []
       for b in user_calendars.get(user_id, []):
           s = parse_iso_datetime(b["start"])
           e = parse_iso_datetime(b["end"])
           intervals.append((s, e))
       normalized_busy[user_id] = intervals


   options_by_key: Dict[tuple[str, str], MeetTimeOption] = {}


   # 2) Loop over each potential time block
   for block in request["potential_time_blocks"]:
       block_start_date = date.fromisoformat(block["start_date"])
       block_end_date = date.fromisoformat(block["end_date"])


       start_h, start_m = map(int, block["start_time"].split(":"))
       end_h, end_m = map(int, block["end_time"].split(":"))


       window_start_time = time(hour=start_h, minute=start_m)
       window_end_time = time(hour=end_h, minute=end_m)


       # 3) Generate candidate slots for each day in this block
       current_date = block_start_date
       while current_date <= block_end_date:
           day_window_start = build_datetime(current_date, window_start_time)
           day_window_end = build_datetime(current_date, window_end_time)


           slot_start = day_window_start


           # 🔹 Align first slot to grid (e.g., minutes 0 or 30)
           minute_mod = slot_start.minute % slot_step_minutes
           if minute_mod != 0:
               slot_start += timedelta(minutes=(slot_step_minutes - minute_mod))


           while slot_start + duration <= day_window_end:
               slot_end = slot_start + duration


               free_users: List[str] = []
               busy_users: List[str] = []


               # 4) Check each participant
               for user_id in participant_ids:
                   is_busy = False
                   for busy_start, busy_end in normalized_busy.get(user_id, []):
                       if overlap(slot_start, slot_end, busy_start, busy_end):
                           is_busy = True
                           break
                   if is_busy:
                       busy_users.append(user_id)
                   else:
                       free_users.append(user_id)


               free_count = len(free_users)


               if free_count == 0:
                   slot_start += slot_step
                   continue


               # 5) Score: base = free_count, with small bonus for on-the-hour starts
               score = float(free_count)
               if slot_start.minute == 0:
                   score += 0.2  # prefer xx:00 slightly more than xx:30


               start_str = slot_start.isoformat(timespec="seconds")
               end_str = slot_end.isoformat(timespec="seconds")
               key = (start_str, end_str)


               option: MeetTimeOption = {
                   "start": start_str,
                   "end": end_str,
                   "free_participants": free_users,
                   "busy_participants": busy_users,
                   "free_count": free_count,
                   "score": score,
               }


               # Save if new or better than existing
               existing = options_by_key.get(key)
               if existing is None or score > existing["score"]:
                   options_by_key[key] = option


               slot_start += slot_step


           current_date = current_date + timedelta(days=1)


   # 6) Sort + slice
   candidate_options = list(options_by_key.values())
   candidate_options.sort(
       key=lambda opt: (-opt["free_count"], -opt["score"], opt["start"])
   )


   return candidate_options[:max_options]