import os
import asyncio
import colorsys
from discord.ext import commands
from discord import Intents
from aiohttp import web

BOT_COUNT = 5
ROLE_ID = int(os.getenv("ROLE_ID"))  # Role to apply the rainbow color to
GUILD_ID = int(os.getenv("GUILD_ID"))  # Server where the role exists

TOKENS = [os.getenv(f"DISCORD_TOKEN_{i+1}") for i in range(BOT_COUNT)]
if any(token is None for token in TOKENS):
    raise ValueError("One or more bot tokens are missing in environment variables.")

intents = Intents.default()

async def run_bot(bot_index: int, token: str):
    bot = commands.Bot(command_prefix="!", intents=intents)
    delay = 1.0  # 1 second per bot loop
    steps = 360  # full hue rotation
    hue_offset = (bot_index / BOT_COUNT) % 1.0

    async def cycle_colors():
        hue = hue_offset
        while True:
            guild = bot.get_guild(GUILD_ID)
            if guild is None:
                print(f"[Bot {bot_index+1}] Guild not found.")
                await asyncio.sleep(delay)
                continue

            role = guild.get_role(ROLE_ID)
            if role is None:
                print(f"[Bot {bot_index+1}] Role not found.")
                await asyncio.sleep(delay)
                continue

            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            color_int = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

            try:
                await role.edit(color=color_int, reason="Rainbow color cycle")
            except Exception as e:
                print(f"[Bot {bot_index+1}] Failed to update role color: {e}")

            hue = (hue + (1 / steps)) % 1.0
            await asyncio.sleep(delay)

    @bot.event
    async def on_ready():
        print(f"[Bot {bot_index+1}] Logged in as {bot.user}")
        bot.loop.create_task(cycle_colors())

    await bot.start(token)

async def start_web_server():
    async def handle(request):
        return web.Response(text="Rainbow role bot is running.")
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

async def main():
    await start_web_server()
    tasks = [run_bot(i, token) for i, token in enumerate(TOKENS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
