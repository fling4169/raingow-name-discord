import os
import asyncio
import colorsys
from discord.ext import commands
from discord import Intents
from aiohttp import web

BOT_COUNT = 5
ROLE_ID = int(os.getenv("ROLE_ID"))  # Put your role ID here in your env variables
GUILD_ID = int(os.getenv("GUILD_ID"))  # Put your guild ID here in your env variables

# Get tokens from env: DISCORD_TOKEN_1 ... DISCORD_TOKEN_5
TOKENS = [os.getenv(f"DISCORD_TOKEN_{i+1}") for i in range(BOT_COUNT)]

if any(token is None for token in TOKENS):
    raise ValueError("One or more bot tokens are missing in environment variables.")

intents = Intents.default()

async def color_cycle(bot_index: int, bot_token: str):
    bot = commands.Bot(command_prefix="!", intents=intents)
    await bot.login(bot_token)

    steps = 360  # Total hue steps
    delay = 1.0 / BOT_COUNT  # One change per second, offset evenly
    hue = bot_index / BOT_COUNT  # Offset hue start per bot

    await asyncio.sleep(bot_index * delay)  # Stagger bot start

    @bot.event
    async def on_ready():
        print(f"Bot {bot_index+1} logged in as {bot.user}!")
        nonlocal hue
        while True:
            guild = bot.get_guild(GUILD_ID)
            if guild is None:
                print(f"Bot {bot_index+1}: Guild not found!")
                await asyncio.sleep(delay)
                continue

            role = guild.get_role(ROLE_ID)
            if role is None:
                print(f"Bot {bot_index+1}: Role not found!")
                await asyncio.sleep(delay)
                continue

            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            color_int = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

            try:
                await role.edit(color=color_int, reason="Rainbow role color cycling")
            except Exception as e:
                print(f"Bot {bot_index+1} failed to update role color: {e}")

            hue = (hue + 1 / steps) % 1.0
            await asyncio.sleep(delay)

    await bot.connect()

async def main():
    tasks = [color_cycle(i, token) for i, token in enumerate(TOKENS)]

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
