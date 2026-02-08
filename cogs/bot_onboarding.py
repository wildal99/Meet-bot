import discord
from discord import app_commands
from discord.ext import commands
import google_auth_oauthlib.flow
import os

# This must match exactly what is in your server.py and Google Cloud Console
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/callback')
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="link", description="Connect your Google Calendar to Meetbot")
    async def link(self, interaction: discord.Interaction):
        # 1. Defer the response (so Discord doesn't timeout while we generate the link)
        await interaction.response.defer(ephemeral=True)

        try:
            # 2. Create the Flow from the client secrets
            # This requires 'credentials.json' to be in the main Meetbot folder, 
            # NOT inside the cogs folder.
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES
            )
            flow.redirect_uri = REDIRECT_URI

            # 3. Generate the URL
            # CRITICAL: We pass the user's Discord ID as the 'state'.
            # This is how server.py knows who is logging in.
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=str(interaction.user.id)
            )

            # 4. Send the link
            await interaction.followup.send(
                f"## 🔗 Link your Calendar\n"
                f"Click the link below to authorize Meetbot.\n"
                f"This will allow us to check your availability and schedule meetings.\n\n"
                f"[**Click here to Login with Google**]({authorization_url})",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Onboarding(bot))