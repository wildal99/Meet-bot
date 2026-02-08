import discord
from discord import app_commands
from discord.ext import commands
import datetime
import re

# Import our helper tools
from utils.gemini import parse_schedule_intent
from utils.gcal_helper import check_busy_times
from database import get_user_data

class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="schedule", description="Plan a meeting using AI")
    @app_commands.describe(
        attendees="Mention the people to invite (e.g. @Tito @Vidk)",
        details="Natural language details (e.g. 'Sync next Friday at 2pm for 30 mins')"
    )
    async def schedule(self, interaction: discord.Interaction, attendees: str, details: str):
        # 1. Acknowledge immediately (Buying time for AI & API calls)
        await interaction.response.defer()

        # --- STEP 1: PARSE THE BRAIN (Gemini) ---
        # We send the text to Gemini to get JSON back
        print(f"🤖 Asking Gemini to parse: '{details}'")
        parsed_data = parse_schedule_intent(details)

        if not parsed_data:
            await interaction.followup.send("❌ **I couldn't understand that date/time.**\nTry being more specific, like *'Tomorrow at 2pm'*.")
            return

        # Extract data from Gemini's JSON
        target_date = parsed_data.get('target_date') # YYYY-MM-DD
        start_time = parsed_data.get('start_time')   # HH:MM
        duration = parsed_data.get('duration_minutes', 30)
        summary = parsed_data.get('summary', 'Meeting')

        # Combine into a Python DateTime object
        try:
            start_dt = datetime.datetime.strptime(f"{target_date} {start_time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + datetime.timedelta(minutes=duration)
        except ValueError:
            await interaction.followup.send("❌ **Date Error:** Gemini returned an invalid date format. Please try again.")
            return

        # --- STEP 2: PARSE THE HUMANS (Discord Mentions) ---
        # We need to find all User IDs in the 'attendees' string.
        # Discord sends mentions like <@123456789>. We use Regex to pull the numbers.
        mentioned_ids = re.findall(r'<@!?(\d+)>', attendees)
        
        # Add the Organizer (the person running the command) to the list
        organizer_id = str(interaction.user.id)
        if organizer_id not in mentioned_ids:
            mentioned_ids.append(organizer_id)

        # --- STEP 3: CHECK THE DATABASE (The Gatekeeper) ---
        # We can't check calendars if they haven't linked them!
        missing_users = []
        valid_users = []

        for uid in mentioned_ids:
            user_data = get_user_data(uid)
            if user_data:
                valid_users.append(uid)
            else:
                missing_users.append(f"<@{uid}>")

        if missing_users:
            # STOP HERE if anyone is missing. Public shaming time.
            missing_list = ", ".join(missing_users)
            await interaction.followup.send(
                f"🛑 **Cannot Schedule Yet!**\n"
                f"The following users have not linked their Google Calendar:\n"
                f"{missing_list}\n\n"
                f"Please tell them to run `/link` first!"
            )
            return

        # --- STEP 4: CHECK THE EYES (Google Calendar) ---
        # Convert to ISO format for Google (Assuming UTC for now - Hackathon MVP)
        iso_start = start_dt.isoformat() + "Z"
        iso_end = end_dt.isoformat() + "Z"

        print(f"👀 Checking availability for {len(valid_users)} users...")
        busy_intervals = check_busy_times(valid_users, iso_start, iso_end)

        # --- STEP 5: THE VERDICT (Reply to Discord) ---
        
        # Create a nice Embed
        embed = discord.Embed(
            title=f"📅 {summary}",
            description=f"**Proposed Time:** {target_date} at {start_time} (UTC)\n**Duration:** {duration} mins",
            color=0x5865F2
        )

        if busy_intervals:
            # CONFLICT FOUND
            embed.color = 0xE02B2B # Red
            embed.add_field(name="❌ Status", value="Conflict Found!", inline=False)
            
            conflict_msg = ""
            for conflict in busy_intervals:
                # conflict['user'] is the ID. We format it as <@ID>
                conflict_msg += f"• <@{conflict['user']}> is busy.\n"
            
            embed.add_field(name="Details", value=conflict_msg, inline=False)
            await interaction.followup.send(embed=embed)
        
        else:
            # SUCCESS - EVERYONE IS FREE
            embed.color = 0x57F287 # Green
            embed.add_field(name="✅ Status", value="All attendees are free!", inline=False)
            embed.add_field(name="Attendees", value=attendees, inline=False)
            
            # Add a button (Visual only for now)
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Book Meeting (Coming Soon)", style=discord.ButtonStyle.primary, disabled=True))
            
            await interaction.followup.send(content="✨ **Time Slot Found!**", embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Scheduler(bot))