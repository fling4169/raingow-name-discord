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

async def color_cycle(bot_index: int, token: str):
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Total hue steps and staggered timing
    total_steps = 360
    update_delay = 1.0  # Each bot tries to edit every second

    # Hue offset for each bot to maintain gradience
    hue_step = 1 / total_steps
    start_hue = (bot_index * (1 / BOT_COUNT)) % 1.0
    current_hue = start_hue

    @bot.event
    async def on_ready():
        print(f"Bot {bot_index+1} logged in as {bot.user}")
        nonlocal current_hue
        while True:
            guild = bot.get_guild(GUILD_ID)
            if guild is None:
                print(f"Bot {bot_index+1}: Guild not found!")
                await asyncio.sleep(update_delay)
                continue

            role = guild.get_role(ROLE_ID)
            if role is None:
                print(f"Bot {bot_index+1}: Role not found!")
                await asyncio.sleep(update_delay)
                continue

            # Convert HSV to RGB and then to Discord's color int
            r, g, b = colorsys.hsv_to_rgb(current_hue, 1, 1)
            color = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

            try:
                await role.edit(color=color, reason="Rainbow role update")
            except Exception as e:
                print(f"Bot {bot_index+1} error editing role: {e}")

            # Move hue forward smoothly
            current_hue = (current_hue + hue_step * BOT_COUNT) % 1.0
            await asyncio.sleep(update_delay)

    await bot.start(token)

async def main():
    # Launch all bot tasks
    tasks = [color_cycle(i, token) for i, token in enumerate(TOKENS)]

    # Simple web server to satisfy Render's web service requirement
    async def handle(request):
        return web.Response(text="Rainbow role bots are running.")

    app = web.Application()
    app.add_routes([web.get('/', handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
