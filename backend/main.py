from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from AITools import openRouterCall


class ScheduleRequest(BaseModel):
    text: str


class DateRange(BaseModel):
    start: str
    end: str

class GeminiRequestDetails(BaseModel):
    action: str
    title: str
    durationMin: int
    particpants: [str]
    dateRange: DateRange




app = fastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace "*" with your specific frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

def parseNLQuery(query):
    systemPrompt = """
        You are a secretary responsible for scheduing meetings. Please return only valid json in the following
        format about the details of the natural language meeting request provided:
        {
        "action": "requested_action",
        "title": "meeting_title",
        "duration_minutes": (int) meeting duration in minutes,
        "participants": [a list of meeting participants, by username],
        "potential_dates_and_times": ["block1":{"start_date": "start_date", "start_time": "start_time", "end_date": "end_date", "end_time": "end_time"},
             "block2": {"start_date": "start_date", "start_time": "start_time", "end_date": "end_date", "end_time": "end_time"},... ],
        }
        """

#first request formatted json from AI
@app.post("/schedule")
def schedule(request :ScheduleRequest ):
    requestData = parseNLQuery(request.text)
    print(requestData)
    #query calendar data for participants
    #request for meeting schedule, ideally with "heatmap" of optimality of times
    #return to discord bot
    #optional reschedule???
    #confirm with discord bot, create calendar items