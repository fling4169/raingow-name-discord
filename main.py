import os
import asyncio
import colorsys
from discord.ext import commands
from discord import Intents
from aiohttp import web

BOT_COUNT = 5
ROLE_ID = int(os.getenv("ROLE_ID"))
GUILD_ID = int(os.getenv("GUILD_ID"))
TOKENS = [os.getenv(f"DISCORD_TOKEN_{i+1}") for i in range(BOT_COUNT)]

if any(token is None for token in TOKENS):
    raise ValueError("One or more bot tokens are missing in environment variables.")

intents = Intents.default()

# Constants for the color cycle
STEPS = 360  # Number of distinct colors in the rainbow cycle
DELAY = 1.2  # Time between updates per bot (seconds)

async def color_cycle(bot_index: int, bot_token: str):
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Bot {bot_index+1} logged in as {bot.user}!")
        hue_offset = bot_index / BOT_COUNT
        hue = hue_offset

        while True:
            guild = bot.get_guild(GUILD_ID)
            if guild is None:
                print(f"Bot {bot_index+1}: Guild not found.")
                await asyncio.sleep(DELAY)
                continue

            role = guild.get_role(ROLE_ID)
            if role is None:
                print(f"Bot {bot_index+1}: Role not found.")
                await asyncio.sleep(DELAY)
                continue

            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            color_int = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

            try:
                await role.edit(color=color_int, reason="Rainbow role color cycling")
            except Exception as e:
                print(f"Bot {bot_index+1} failed to update role color: {e}")

            hue = (hue + 1 / STEPS) % 1.0
            await asyncio.sleep(DELAY)

    await bot.start(bot_token)

async def main():
    tasks = [color_cycle(i, token) for i, token in enumerate(TOKENS)]

    # Web server to keep Render happy
    async def handle(request):
        return web.Response(text="Rainbow role bots running.")

    app = web.Application()
    app.add_routes([web.get('/', handle)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
