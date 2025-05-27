import os
import asyncio
import colorsys
import logging
from discord.ext import commands, tasks
from discord import Intents
from aiohttp import web

logging.basicConfig(level=logging.INFO)

BOT_COUNT = 5
ROLE_ID = int(os.getenv("ROLE_ID"))
GUILD_ID = int(os.getenv("GUILD_ID"))
TOKENS = [os.getenv(f"DISCORD_TOKEN_{i+1}") for i in range(BOT_COUNT)]

if any(token is None for token in TOKENS):
    raise ValueError("One or more bot tokens are missing in environment variables.")

intents = Intents.default()

def hsv_to_discord_color(h: float) -> int:
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, 1, 1)
    return (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

async def run_bot(bot_index: int, token: str):
    bot = commands.Bot(command_prefix="!", intents=intents)
    delay = 1.0
    steps = 360
    hue_step = 1 / steps
    hue_offset = bot_index * (1.0 / BOT_COUNT)
    hue = hue_offset

    @bot.event
    async def on_ready():
        logging.info(f"[Bot {bot_index+1}] Logged in as {bot.user}")
        change_color.start()

    @tasks.loop(seconds=delay)
    async def change_color():
        nonlocal hue
        try:
            guild = bot.get_guild(GUILD_ID)
            if guild is None:
                logging.warning(f"[Bot {bot_index+1}] Guild not found.")
                return

            role = guild.get_role(ROLE_ID)
            if role is None:
                logging.warning(f"[Bot {bot_index+1}] Role not found.")
                return

            color = hsv_to_discord_color(hue)
            await role.edit(color=color, reason="Rainbow cycle update")

            hue = (hue + hue_step * BOT_COUNT) % 1.0  # Step entire hue wheel evenly across bots
        except Exception as e:
            logging.error(f"[Bot {bot_index+1}] Failed to change color: {e}")

    await bot.start(token)

async def main():
    # Start all bots concurrently
    bot_tasks = [run_bot(i, token) for i, token in enumerate(TOKENS)]

    # Web server to keep Render service awake
    async def handle(request):
        return web.Response(text="Rainbow role bots running.")

    app = web.Application()
    app.add_routes([web.get("/", handle)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

    await asyncio.gather(*bot_tasks)

if __name__ == "__main__":
    asyncio.run(main())
