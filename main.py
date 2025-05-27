import os
import asyncio
import colorsys
from aiohttp import web
from discord.ext import commands
from discord import Intents
import time

BOT_COUNT = 5
ROLE_ID = int(os.getenv("ROLE_ID"))
GUILD_ID = int(os.getenv("GUILD_ID"))

TOKENS = [os.getenv(f"DISCORD_TOKEN_{i+1}") for i in range(BOT_COUNT)]
if any(token is None for token in TOKENS):
    raise ValueError("Missing one or more DISCORD_TOKENs in environment variables.")

intents = Intents.default()

shared_hue = 0.0
hue_lock = asyncio.Lock()
last_update_time = time.time()

async def watchdog():
    global last_update_time
    while True:
        await asyncio.sleep(10)
        elapsed = time.time() - last_update_time
        if elapsed > 20:
            print(f"[WATCHDOG] Warning: No color update in {int(elapsed)} seconds. Bots may be stalled.")

async def color_cycle(bot_index: int, bot_token: str):
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Bot {bot_index + 1} logged in as {bot.user}")
        global shared_hue, last_update_time
        steps = 360
        delay = 1.0

        while True:
            async with hue_lock:
                hue = shared_hue
                shared_hue = (shared_hue + (1 / steps)) % 1.0

            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            color_int = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

            guild = bot.get_guild(GUILD_ID)
            if not guild:
                print(f"[Bot {bot_index + 1}] Guild not found")
                await asyncio.sleep(delay)
                continue

            role = guild.get_role(ROLE_ID)
            if not role:
                print(f"[Bot {bot_index + 1}] Role not found")
                await asyncio.sleep(delay)
                continue

            try:
                await role.edit(color=color_int, reason="Rainbow color update")
                last_update_time = time.time()
                print(f"[Bot {bot_index + 1}] Updated color to {color_int:#06x}")
            except Exception as e:
                print(f"[Bot {bot_index + 1}] Error updating role color: {e}")

            await asyncio.sleep(delay)

    await bot.start(bot_token)

async def main():
    tasks = [color_cycle(i, token) for i, token in enumerate(TOKENS)]
    tasks.append(watchdog())

    # Keepalive web server for Render
    async def handle(request):
        return web.Response(text="Rainbow role bot running.")

    app = web.Application()
    app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
