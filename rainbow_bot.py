import os
import asyncio
import discord
from discord.ext import commands

class RainbowBot(commands.Bot):
    def __init__(self, token):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        self.token = token

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    def run_bot(self):
        if not self.token or self.token == "your-token":
            raise ValueError("Discord bot token is missing or invalid. Please set the DISCORD_TOKEN environment variable correctly.")
        self.run(self.token)

if __name__ == "__main__":
    # Get token from environment variable
    token = os.getenv("DISCORD_TOKEN")

    # Run bot
    bot = RainbowBot(token)
    try:
        bot.run_bot()
    except Exception as e:
        print(f"Bot failed to start: {e}")
