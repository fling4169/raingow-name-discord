import os
import asyncio
import colorsys
from aiohttp import web
from discord.ext import commands
from discord import Intents

BOT_COUNT = 5
ROLE_ID = int(os.getenv("ROLE_ID"))
GUILD_ID = int(os.getenv("GUILD_ID"))

TOKENS = [os.getenv(f"DISCORD_TOKEN_{i+1}") for i in range(BOT_COUNT)]
if any(token is None for token in TOKENS):
    raise ValueError("Missing one or more DISCORD_TOKENs in environment variables.")

intents = Intents.default()

async def color_cycle(bot_index: int, bot_token: str):
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"✅ Bot {bot_index + 1} logged in as {bot.user}")
        steps = 360
        delay = 1.0

        # Use a unique hue offset for each bot
        hue = (bot_index / BOT_COUNT) % 1.0

        while True:
            try:
                # Calculate RGB color from hue
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

                await role.edit(color=color_int, reason="Rainbow color update")
                print(f"[Bot {bot_index + 1}] Updated color to {color_int:#06x}")

                # Advance hue
                hue = (hue + (1 / steps)) % 1.0
                await asyncio.sleep(delay)

            except Exception as e:
                print(f"[Bot {bot_index + 1}] ERROR: {e}")
                await asyncio.sleep(5)

    try:
        await bot.start(bot_token)
    except Exception as e:
        print(f"[Bot {bot_index + 1}] FAILED TO START: {e}")

async def main():
    tasks = [color_cycle(i, token) for i, token in enumerate(TOKENS)]

    # Keepalive web server
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
