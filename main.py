import discord
import asyncio
import colorsys
import os
from dotenv import load_dotenv
from flask import Flask
import threading

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "Rainbow Role Bot is running!"

# Each bot token from environment
TOKENS = [os.getenv(f'DISCORD_TOKEN_{i}') for i in range(1, 6)]

# Role and Guild settings
GUILD_ID = YOUR_GUILD_ID_HERE  # Replace with your server ID
ROLE_ID = YOUR_ROLE_ID_HERE    # Replace with the role ID to color cycle

# Rainbow settings
STEPS = 360  # Total steps in full hue cycle
INTERVAL = 1  # Total update interval in seconds (1 second per update)

def hsv_to_rgb_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return discord.Colour.from_rgb(int(r * 255), int(g * 255), int(b * 255))

async def rainbow_loop(bot, offset):
    await bot.wait_until_ready()
    guild = bot.get_guild(GUILD_ID)
    role = guild.get_role(ROLE_ID)
    if role is None:
        print("Role not found.")
        return

    hue = offset
    while not bot.is_closed():
        color = hsv_to_rgb_hex(hue, 1, 1)
        try:
            await role.edit(colour=color, reason="Rainbow effect")
        except Exception as e:
            print(f"Failed to update role color: {e}")
        hue = (hue + 1 / STEPS) % 1.0
        await asyncio.sleep(INTERVAL)

async def run_bot(token, offset):
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")

    bot.loop.create_task(rainbow_loop(bot, offset))
    await bot.start(token)

async def main():
    num_bots = len(TOKENS)
    tasks = []

    for i, token in enumerate(TOKENS):
        if token:
            offset = i / num_bots  # Evenly spaced hue offsets
            tasks.append(run_bot(token, offset))
        else:
            print(f"Token {i+1} is missing!")

    await asyncio.gather(*tasks)

def start_web():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=start_web).start()
    asyncio.run(main())
