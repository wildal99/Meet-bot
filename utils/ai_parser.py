import os
import json
import datetime
import google.generativeai as genai

# Configure the API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def parse_schedule_intent(prompt_text, user_timezone="UTC"):
    """
    Uses Gemini to extract date, time, and duration from natural language.
    Returns a JSON object.
    """
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found.")
        return None

    # Get current context so Gemini knows what "Next Friday" means
    now = datetime.datetime.now()
    current_date_str = now.strftime("%Y-%m-%d")
    current_day = now.strftime("%A")

    # The System Instruction (The "Brain's" Job Description)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    system_prompt = f"""
    You are a scheduling assistant. Your job is to extract scheduling details from a user's prompt into JSON.
    
    Context:
    - Today is: {current_day}, {current_date_str}
    - User Timezone: {user_timezone}
    - Default Duration: 30 minutes (if not specified)
    - "Evening" implies: 18:00 (6 PM) start time.
    - "Morning" implies: 09:00 (9 AM) start time.
    - "Afternoon" implies: 13:00 (1 PM) start time.
    
    Task:
    Analyze the prompt: "{prompt_text}"
    
    Return ONLY a raw JSON object (no markdown formatting) with these fields:
    - "target_date": (YYYY-MM-DD format)
    - "start_time": (HH:MM in 24-hour format, e.g., "14:00")
    - "duration_minutes": (integer)
    - "summary": (A short title for the meeting, e.g., "Sync with Tito")
    
    If the prompt is vague (e.g., just "meeting"), assume tomorrow at 10:00 AM.
    """

    try:
        response = model.generate_content(system_prompt)
        # Clean up response (sometimes Gemini wraps JSON in ```json ... ```)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        print("Gemini Response: ")  # Debugging output
        
        return json.loads(cleaned_text)
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return None