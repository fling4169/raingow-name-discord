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

# Shared mutable state for hue
shared = {"hue": 0.0}
hue_lock = asyncio.Lock()
steps = 360  # Number of hue steps in full cycle
update_interval = 1.0  # 1 second per bot update, staggered

async def color_cycle(bot_index: int, bot_token: str):
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Bot {bot_index+1} logged in as {bot.user}")
        
        # Stagger start so bots update every second in order
        await asyncio.sleep(bot_index)

        while True:
            async with hue_lock:
                hue = shared["hue"]
                shared["hue"] = (shared["hue"] + 1 / steps) % 1.0

            # Calculate each bot’s gradient-shifted hue
            bot_hue = (hue + (bot_index / BOT_COUNT)) % 1.0
            r, g, b = colorsys.hsv_to_rgb(bot_hue, 1, 1)
            color_int = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

            guild = bot.get_guild(GUILD_ID)
            if guild:
                role = guild.get_role(ROLE_ID)
                if role:
                    try:
                        await role.edit(color=color_int, reason="Rainbow role update")
                    except Exception as e:
                        print(f"Bot {bot_index+1} failed to update role color: {e}")
                else:
                    print(f"Bot {bot_index+1}: Role not found")
            else:
                print(f"Bot {bot_index+1}: Guild not found")

            # Wait BOT_COUNT seconds before this bot runs again
            await asyncio.sleep(BOT_COUNT * update_interval)

    await bot.login(bot_token)
    await bot.connect()

async def main():
    tasks = [color_cycle(i, token) for i, token in enumerate(TOKENS)]

    # Render health check web server
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
