import discord
from discord.ext import commands, tasks
import itertools
import asyncio
from rainbow_colors import generate_rainbow_colors

class RainbowBot:
    def __init__(self, token, role_id, offset_seconds):
        self.token = token
        self.role_id = role_id
        self.offset = offset_seconds
        self.color_cycle = itertools.cycle(generate_rainbow_colors(100))
        self.intents = discord.Intents.default()
        self.intents.guilds = True
        self.bot = commands.Bot(command_prefix="!", intents=self.intents)

        self.bot.event(self.on_ready)
        self.change_color_loop = tasks.loop(seconds=5)(self.change_color)

    async def on_ready(self):
        print(f"✅ {self.bot.user} ready with {self.offset}s offset")
        await asyncio.sleep(self.offset)
        self.change_color_loop.start()

    async def change_color(self):
        for guild in self.bot.guilds:
            role = guild.get_role(self.role_id)
            if role:
                try:
                    await role.edit(color=next(self.color_cycle))
                except Exception as e:
                    print(f"[{self.bot.user}] Error: {e}")

    def run(self):
        self.bot.run(self.token)
