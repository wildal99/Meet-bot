from dotenv import load_dotenv


from datetime import datetime

import requests

import json
import os


def openRouterCall(message, systemPrompt):
    load_dotenv()
    openRouterKey = os.getenv('OR_API_KEY')
    print("or api key: ", openRouterKey)

    #get todays date to handle vauge dates, since gemini doesnt know what day is??
    now = datetime.now()

# First API call with reasoning
    response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {openRouterKey}",
        "Content-Type": "application/json",
    },
    data=json.dumps({
        "model": "google/gemini-3-flash-preview",
        "messages": [
            {
                "role": "system", "content": systemPrompt + f"Today is {now}"
            },
            {
            "role": "assistant",
            "content": message
            }
        ],
        "reasoning": {"enabled": True}
    })
    )

    # Extract the assistant message with reasoning_details
    response = response.json()
    response = response['choices'][0]['message']

    # Preserve the assistant message with reasoning_details
    reasoning = [
    {"role": "system", "content": systemPrompt},
    {
        "role": "assistant",
        "content": response.get('content'),
        "reasoning_details": response.get('reasoning_details')  # Pass back unmodified
    },
    ]

    '''
    # Second API call - model continues reasoning from where it left off
    response2 = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps({
        "model": "google/gemini-3-flash-preview",
        "messages": messages,  # Includes preserved reasoning_details
        "reasoning": {"enabled": False}
    })
    )
    '''
    print(response)
    return response

def getParticipantsDiscord(query):
    now = datetime.now()
    systemPrompt = """You are a secretary responsible for scheduing meetings. Please return a list of all intended participants, 
    and addiitonal scheduling instructions.
    You are to return only valid json in the following format: 
    {
        "usernames": [{"discord_name_1": "<participant's discord name>"}, ...],
        "instructions": "<Additional instructions for scheduling. If a specific date is not given, do not add a specific date>" 
    }
    """

    response = openRouterCall(query, systemPrompt)
    print(response)

    return response['content']


def getTimes(query, userCalendars):
    systemPrompt = """
        You are a secretary responsible for scheduing meetings. Please return only valid json in the following
        format about the details of meeting times. When you are unable to schedule all participants, please still return possible options,
        and who is able to attend.:
     {
    "action": "requested_action",
    "title": "meeting_title",
    "duration_minutes": 30,
    "potential_meeting_dates_and_times": [
        {
        "start_date": "YYYY-MM-DD",
        "start_time": "HH:MM",
        "end_date": "YYYY-MM-DD",
        "end_time": "HH:MM",
        "participants_available": [
            "<name OR @discord_username>",
            "<name OR @discord_username>"
        ]
        },
        {
        "start_date": "YYYY-MM-DD",
        "start_time": "HH:MM",
        "end_date": "YYYY-MM-DD",
        "end_time": "HH:MM",
        "participants_available": [
            "<name OR @discord_username>",
            "<name OR @discord_username>"
        ]
        }
    ]
    }
    """

    meetingTimesJson = openRouterCall(query, systemPrompt)

def main():
    samplePrompt = f"Lets schedule a meeting for a sunday afternoon between @jimBob,  @BoPeep, @conor, and @super. @super and @jimbob should be able to attend."

    discordUsers = getParticipantsDiscord(samplePrompt)
    print(discordUsers)

if __name__ == "__main__":
    main()

