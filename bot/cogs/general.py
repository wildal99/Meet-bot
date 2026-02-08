import discord
from discord.ext import commands
from discord import app_commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # This decorator creates a slash command
    @app_commands.command(name="ping", description="Check if Meetbot is alive")
    async def ping(self, interaction: discord.Interaction):
        # Calculate latency in milliseconds
        latency = round(self.bot.latency * 1000)
        
        # Respond to the user
        await interaction.response.send_message(f"Meetbot is alive ({latency}ms)")

# This function is required for bot.py to load this file
async def setup(bot):
    await bot.add_cog(General(bot))