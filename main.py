import os
import asyncio
import threading
import colorsys
from flask import Flask
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # Only needed if you use a .env file locally

# Flask app to keep Render happy
app = Flask("")

@app.route("/")
def home():
    return "Rainbow role bot is running."

def run_flask():
    app.run(host="0.0.0.0", port=8000)

# Helper: Convert HSV color to Discord color object
def hsv_to_discord_color(h, s=1.0, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return discord.Color.from_rgb(int(r * 255), int(g * 255), int(b * 255))

async def rainbow_role_task(bot, guild_id, role_id):
    await bot.wait_until_ready()
    guild = bot.get_guild(guild_id)
    if not guild:
        print(f"[{bot.user}] Guild {guild_id} not found.")
        return
    role = guild.get_role(role_id)
    if not role:
        print(f"[{bot.user}] Role {role_id} not found.")
        return

    h = 0.0
    while not bot.is_closed():
        color = hsv_to_discord_color(h)
        try:
            await role.edit(color=color, reason="Rainbow role color cycling")
            print(f"[{bot.user}] Updated role color to hue {h:.2f}")
        except Exception as e:
            print(f"[{bot.user}] Failed to update role color: {e}")

        h += 0.005  # Smaller increments for smoother transitions
        if h >= 1.0:
            h = 0.0
        await asyncio.sleep(5)  # Adjust delay for speed of color change

async def run_bot(token, guild_id, role_id):
    intents = discord.Intents.default()
    intents.guilds = True
    intents.guild_messages = True
    intents.guilds = True
    intents.guild_messages = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    # Start the rainbow task when the bot is ready
    @bot.event
    async def on_ready():
        print(f"{bot.user} has connected.")
        # Start color cycling task in background
        bot.loop.create_task(rainbow_role_task(bot, guild_id, role_id))

    await bot.start(token)

async def main():
    # Start Flask in separate thread so Render web service doesn't crash
    threading.Thread(target=run_flask, daemon=True).start()

    # Your guild and role IDs here (replace with your actual IDs)
    GUILD_ID = int(os.environ.get("GUILD_ID"))
    ROLE_ID = int(os.environ.get("ROLE_ID"))

    # Collect tokens from environment variables
    tokens = []
    for i in range(1, 6):
        t = os.environ.get(f"DISCORD_TOKEN_{i}")
        if t:
            tokens.append(t)
        else:
            print(f"Warning: DISCORD_TOKEN_{i} not found in environment variables.")

    if not tokens:
        print("No Discord tokens found. Exiting.")
        return

    # Run all bots concurrently
    tasks = [run_bot(token, GUILD_ID, ROLE_ID) for token in tokens]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
