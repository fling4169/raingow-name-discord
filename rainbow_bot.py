import os
import asyncio
import discord
from discord.ext import commands, tasks
from rainbow_colors import generate_rainbow_colors

class RainbowBot(commands.Bot):
    def __init__(self, token, role_id, offset_seconds=0):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        self.token = token
        self.role_id = role_id
        self.offset_seconds = offset_seconds
        self.color_index = 0
        self.colors = generate_rainbow_colors()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        if not self.change_color_loop.is_running():
            await asyncio.sleep(self.offset_seconds)
            self.change_color_loop.start()

    @tasks.loop(seconds=10.0)
    async def change_color_loop(self):
        for guild in self.guilds:
            role = guild.get_role(self.role_id)
            if role:
                try:
                    await role.edit(color=self.colors[self.color_index])
                except discord.Forbidden:
                    print(f"Permission denied to edit role in {guild.name}")
                except Exception as e:
                    print(f"Error editing role in {guild.name}: {e}")
        self.color_index = (self.color_index + 1) % len(self.colors)

    def run_bot(self):
        if not self.token or self.token == "your-token":
            raise ValueError("Discord bot token is missing or invalid.")
        self.run(self.token)
