import os
import google_auth_oauthlib.flow
from flask import Flask, request, redirect
from database import save_user_token  # Import our function from step 1

# --- CONFIGURATION ---
app = Flask(__name__)

# This must match the URI you added in Google Cloud Console
# For local testing, it's usually this:
# If the environment variable exists (Cloud), use it. Otherwise use localhost (Testing).
# PROD: Get URL from environment. DEV: Fallback to localhost.
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/callback')

# The permissions we are asking for
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# This allows us to use HTTP (not HTTPS) for local testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

@app.route('/')
def home():
    """Simple check to see if server is running."""
    return "Meetbot Server is Online! 🤖"

@app.route('/callback')
def callback():
    """
    Google redirects the user here after they log in.
    The URL will look like: /callback?state=12345&code=4/0Ad...
    """
    # 1. Get the State (Discord User ID)
    # We passed this to Google when we created the link. Now it comes back.
    state = request.args.get('state')
    
    if not state:
        return "Error: No state received. I don't know who you are!", 400

    # 2. specific 'flow' object to handle the exchange
    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'credentials.json',
            scopes=SCOPES,
            state=state
        )
        flow.redirect_uri = REDIRECT_URI

        # 3. Exchange the 'code' in the URL for real Tokens
        # request.url contains the full address with the ?code=... part
        authorization_response = request.url
        
        # Fetch the tokens from Google
        flow.fetch_token(authorization_response=authorization_response)
        
        # 4. Extract the credentials
        credentials = flow.credentials
        
        # CRITICAL: We need the 'refresh_token'.
        # Google only sends this the FIRST time a user authorizes.
        # If it's None, it means the user was already linked before.
        # We save it to the DB.
        if credentials.refresh_token:
            save_user_token(discord_id=state, refresh_token=credentials.refresh_token)
            return f"<h1>Success!</h1><p>Discord User <b>{state}</b> is now linked to Meetbot.</p><p>You can close this window.</p>"
        else:
            # If we didn't get a refresh token, usually we still update the email/ID logic
            # For now, we just assume it worked if no error.
            save_user_token(discord_id=state, refresh_token="EXISTING_TOKEN_REUSED") 
            return f"<h1>Re-linked!</h1><p>Welcome back, User {state}.</p>"

    except Exception as e:
        return f"<h2>An error occurred:</h2><p>{e}</p>", 500

if __name__ == '__main__':
    # Run the server on port 5000
    print(f"Server running on {REDIRECT_URI}")
    app.run(port=5000, debug=True)