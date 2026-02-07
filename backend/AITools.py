from dotenv import load_dotenv
import os

import requests
import json

from datetime import datetime



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
    return response, reasoning

def main():
    load_dotenv()
    openRouterKey = os.getenv('OR_API_KEY')

    systemPrompt = """
        You are a secretary responsible for scheduing meetings. You are not to create a final meeting time. Only return potential meeting times, and include several, if possible.
        Please return only valid json in the following
        format about the details of the natural language provided using ISO standard date and time format:
        {
        "requested_action": "schedule_meeting",
        "title": "<meeting_title>",
        "duration_minutes": (int) meeting duration in minutes,
        "participants": [please list meeting participants],
        "potential_dates_and_times": ["block1":{"start_date": <start_date>, "start_time": "start_time", "end_date": "end_date", "end_time": "end_time"},
             "block2": {"start_date": "start_date", "start_time": "start_time", "end_date": "end_date", "end_time": "end_time"},... ],
        }
        """

    openRouterCall("Lets schedule a meeting with tom and joe.", systemPrompt)



if __name__ == "__main__":
    print("calling main")
    main()