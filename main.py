# main.py
from pprint import pprint
from scheduler import generate_meeting_options, MeetingRequest
from gcal_demo import fetch_busy_from_gcal

# Toggle this to switch between demo + real Google Calendar
DEMO_MODE = True


def run_demo_mode() -> None:
    """
    Old-style demo with hard-coded calendars (u1, u2, u3).
    Great for showing the algorithm without needing Google auth.
    """
    timezone = "America/Toronto"

    # Meeting request, now using potential_time_blocks instead of date_range/time_window
    request: MeetingRequest = {
        "title": "Project Sync",
        "duration_minutes": 60,
        "timezone": timezone,
        "participant_ids": ["u1", "u2", "u3"],
        "potential_time_blocks": [
            {
                "start_date": "2026-02-10",
                "end_date": "2026-02-12",
                "start_time": "17:00",  # 5pm local
                "end_time": "22:00",    # 10pm local
            }
        ],
    }

    # Same mock calendars you were using before
    user_calendars = {
        "u1": [
            {"start": "2026-02-10T18:00:00", "end": "2026-02-10T21:30:00"},
        ],
        "u2": [
            {"start": "2026-02-10T17:00:00", "end": "2026-02-10T18:00:00"},
            {"start": "2026-02-11T17:00:00", "end": "2026-02-11T22:00:00"},
        ],
        "u3": [
            {"start": "2026-02-12T19:00:00", "end": "2026-02-12T20:00:00"},
        ],
    }

    options = generate_meeting_options(request, user_calendars, max_options=5)
    print("\n=== DEMO MODE OPTIONS ===")
    pprint(options)


def run_gcal_mode() -> None:
    """
    Real mode: pull Seun's busy times from Google Calendar
    and feed them into the scheduler.
    """
    timezone = "America/Toronto"

    # 1) Get busy times from your real Google Calendar
    start_iso = "2026-02-02T00:00:00-05:00"
    end_iso = "2026-02-08T23:59:59-05:00"

    seun_busy = fetch_busy_from_gcal(start_iso, end_iso, timezone=timezone)

    # 2) Meeting request using the new potential_time_blocks structure
    request: MeetingRequest = {
        "title": "Project Sync",
        "duration_minutes": 60,
        "timezone": timezone,
        "participant_ids": ["seun"],   # later: ["seun", "tito", "deji", ...]
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
    print("\n=== GCAL MODE OPTIONS (REAL BUSY TIMES) ===")
    pprint(options)


if __name__ == "__main__":
    if DEMO_MODE:
        run_demo_mode()
    else:
        run_gcal_mode()
