import os
import requests
import google_auth_oauthlib.flow
from flask import Flask, request, redirect
# FIX 1: Import init_db so we can create tables
from database import save_user_token, init_db

app = Flask(__name__)

REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/callback')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# FIX 2: Create the database table immediately when server starts
with app.app_context():
    print("Checking database tables...")
    init_db()

def send_discord_success(channel_id, user_id):
    if not DISCORD_TOKEN or not channel_id:
        return
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}", "Content-Type": "application/json"}
    payload = {"content": f"🎉 **Success!** <@{user_id}> has linked their Google Calendar!"}
    requests.post(url, json=payload, headers=headers)

@app.route('/')
def home():
    return "Meetbot Server is Online! 🤖"

@app.route('/callback')
def callback():
    state_str = request.args.get('state')
    if not state_str:
        return "Error: No state received.", 400

    try:
        if '_' in state_str:
            user_id, channel_id = state_str.split('_')
        else:
            user_id = state_str
            channel_id = None

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'credentials.json', scopes=SCOPES, state=state_str
        )
        flow.redirect_uri = REDIRECT_URI
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        refresh_token = credentials.refresh_token if credentials.refresh_token else "EXISTING_TOKEN_REUSED"
        save_user_token(discord_id=user_id, refresh_token=refresh_token)

        if channel_id:
            send_discord_success(channel_id, user_id)

        # FIX 3: ADDED THE MISSING RETURN STATEMENT
        return f"""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #43b581;">Success!</h1>
                <p>Discord User <b>{user_id}</b> is now linked.</p>
                <p>You can close this window.</p>
            </body>
        </html>
        """

    except Exception as e:
        print(f"❌ ERROR in callback: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)