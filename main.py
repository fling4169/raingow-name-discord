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
intents.guilds = True
intents.guild_messages = True

steps = 360  # total hue steps
hue_state = [i * (1 / BOT_COUNT) for i in range(BOT_COUNT)]
delay = 1.0  # 1 update per second total

async def color_cycle(bot_index: int, token: str):
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"Bot {bot_index + 1} logged in as {bot.user}")

        await asyncio.sleep(bot_index)  # staggered start

        while True:
            guild = bot.get_guild(GUILD_ID)
            if not guild:
                print(f"Bot {bot_index + 1}: Guild not found")
                await asyncio.sleep(delay * BOT_COUNT)
                continue

            role = guild.get_role(ROLE_ID)
            if not role:
                print(f"Bot {bot_index + 1}: Role not found")
                await asyncio.sleep(delay * BOT_COUNT)
                continue

            # Use shared hue_state to keep continuity
            hue = hue_state[bot_index]
            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            color_int = (int(r * 255) << 16) + (int(g * 255) << 8) + int(b * 255)

            try:
                await role.edit(color=color_int, reason="Rainbow cycle")
            except Exception as e:
                print(f"Bot {bot_index + 1} failed to edit role: {e}")

            # Advance hue for this bot only
            hue = (hue + 1 / steps) % 1.0
            hue_state[bot_index] = hue

            await asyncio.sleep(delay * BOT_COUNT)  # Each bot updates every 5s

    await bot.connect(token)


async def main():
    tasks = [color_cycle(i, token) for i, token in enumerate(TOKENS)]

    # Web server to keep Render alive
    async def handle(request):
        return web.Response(text="Rainbow bot is alive.")

    app = web.Application()
    app.add_routes([web.get('/', handle)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
