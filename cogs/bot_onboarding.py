import discord
from discord import app_commands
from discord.ext import commands
import google_auth_oauthlib.flow
import os
# FIX 1: Import the correct function from database.py
from database import get_user_data

REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/callback')
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="link", description="Connect your Google Calendar to Meetbot")
    async def link(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES
            )
            flow.redirect_uri = REDIRECT_URI
            
            combined_state = f"{interaction.user.id}_{interaction.channel_id}"

            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=combined_state,
                prompt='consent'
            )

            await interaction.followup.send(
                f"## 🔗 Link your Calendar\n"
                f"Click below to authorize Meetbot:\n"
                f"[**Click here to Login with Google**]({authorization_url})",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
    
    @app_commands.command(name="status", description="Check if you are linked to Meetbot")
    async def status(self, interaction: discord.Interaction):
        # FIX 2: Use get_user_data (not get_user_token)
        user_data = get_user_data(interaction.user.id)
        
        if user_data:
            await interaction.response.send_message(
                f"✅ **Verified:** {interaction.user.mention} has linked their calendar!",
                ephemeral=False 
            )
        else:
            await interaction.response.send_message(
                f"❌ **Not Linked:** You haven't linked your calendar yet. Use `/link` to get started.",
                ephemeral=False
            )
    
async def setup(bot):
    await bot.add_cog(Onboarding(bot))