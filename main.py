import os
import asyncio
import colorsys
from discord.ext import commands
from discord import Intents
from aiohttp import web

BOT_COUNT = 5
ROLE_ID = int(os.getenv("ROLE_ID"))  # Role ID from environment
GUILD_ID = int(os.getenv("GUILD_ID"))  # Guild ID from environment

# Load tokens from environment
TOKENS = [os.getenv(f"DISCORD_TOKEN_{i + 1}") for i in range(BOT_COUNT)]
if any(token is None for token in TOKENS):
    raise ValueError("One or more DISCORD_TOKEN_X environment variables are missing.")

intents = Intents.default()

async def color_cycle(bot_index: int, bot_token: str):
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Bot {bot_index + 1} logged in as {bot.user}")
        delay = 1.0  # seconds
        steps = 360
        hue = bot_index * (1 / BOT_COUNT)

        # Stagger start
        await asyncio.sleep(bot_index * (delay / BOT_COUNT))

        while True:
            guild = bot.get_guild(GUILD_ID)
            if guild is None:
                print(f"Bot {bot_index + 1}: Guild not found.")
                await asyncio.sleep(delay)
                continue

            role = guild.get_role(ROLE_ID)
            if role is None:
                print(f"Bot {bot_index + 1}: Role not found.")
                await asyncio.sleep(delay)
                continue

            # Convert HSV to RGB and then to Discord integer color
            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            discord_color = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

            try:
                await role.edit(color=discord_color, reason="Rainbow cycle")
            except Exception as e:
                print(f"Bot {bot_index + 1}: Failed to edit role color: {e}")

            hue = (hue + 1 / steps) % 1.0
            await asyncio.sleep(delay)

    await bot.login(bot_token)
    await bot.connect()

async def main():
    # Launch web server for Render
    async def handle(request):
        return web.Response(text="Rainbow role bots running.")

    app = web.Application()
    app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8000)
    await site.start()

    # Start all bots
    tasks = [color_cycle(i, token) for i, token in enumerate(TOKENS)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
