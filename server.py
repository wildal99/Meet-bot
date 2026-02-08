import os
import requests  # standard library to make HTTP requests
import google_auth_oauthlib.flow
from flask import Flask, request, redirect
from database import save_user_token

# --- CONFIGURATION ---
app = Flask(__name__)

# Environment Variables
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/callback')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') # Needed to send messages back to Discord

# The permissions we are asking for
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Allow HTTP for local testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def send_discord_success(channel_id, user_id):
    """
    Sends a public success message to the Discord channel where the command started.
    """
    if not DISCORD_TOKEN or not channel_id:
        print("Error: Missing Discord Token or Channel ID")
        return

    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # The message content
    payload = {
        "content": f"🎉 **Success!** <@{user_id}> has successfully linked their Google Calendar. You are ready to use `/schedule`!"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Failed to send Discord message: {response.text}")

@app.route('/')
def home():
    """Simple check to see if server is running."""
    return "Meetbot Server is Online! 🤖"

@app.route('/callback')
def callback():
    """
    Google redirects the user here after they log in.
    """
    # 1. Get the State (Expected format: "UserID_ChannelID")
    state_str = request.args.get('state')
    
    if not state_str:
        return "Error: No state received.", 400

    # Split the state to get User ID and Channel ID
    try:
        # If state has an underscore, split it. If not, assume it's just User ID (backward compatibility)
        if '_' in state_str:
            user_id, channel_id = state_str.split('_')
        else:
            user_id = state_str
            channel_id = None
    except ValueError:
        return "Error: Invalid state format", 400

    try:
        # 2. Setup the Flow
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'credentials.json',
            scopes=SCOPES,
            state=state_str
        )
        flow.redirect_uri = REDIRECT_URI

        # 3. Exchange the 'code' for Tokens
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        # 4. Save to Database (Using only the User ID, not the full state string)
        # We assume save_user_token takes (discord_id, refresh_token)
        if credentials.refresh_token:
            save_user_token(discord_id=user_id, refresh_token=credentials.refresh_token)
        else:
            # If re-linking, Google might not send a new refresh token unless we force it.
            # We treat this as a success for now.
            save_user_token(discord_id=user_id, refresh_token="EXISTING_TOKEN_REUSED")

        # 5. Send the Success Message to Discord
        if channel_id:
            send_discord_success(channel_id, user_id)

    except Exception as e:
        return f"<h2>An error occurred:</h2><p>{e}</p>", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # We use '0.0.0.0' to ensure it listens on all interfaces (crucial for Render)
    app.run(host='0.0.0.0', port=port)