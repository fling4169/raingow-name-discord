import discord
from discord.ext import commands, tasks
import itertools
import colorsys
from flask import Flask
import threading
import os

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_ID = 123456789012345678  # <<< Paste your actual role ID here

# Generate 100 rainbow colors
def generate_rainbow_colors(n=100):
    return [
        discord.Color.from_rgb(*[int(c * 255) for c in colorsys.hsv_to_rgb(i / n, 1, 1)])
        for i in range(n)
    ]

rainbow_colors = itertools.cycle(generate_rainbow_colors(100))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    change_color.start()

@tasks.loop(seconds=4)
async def change_color():
    for guild in bot.guilds:
        role = guild.get_role(ROLE_ID)
        if role:
            try:
                await role.edit(color=next(rainbow_colors))
            except discord.Forbidden:
                print(f"Missing permissions to edit role in {guild.name}")
            except Exception as e:
                print(f"Error editing role in {guild.name}: {e}")

# Flask server for uptime pings
app = Flask("")

@app.route("/")
def home():
    return "🌈 Rainbow Role Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def start_flask():
    thread = threading.Thread(target=run_flask)
    thread.start()

start_flask()
bot.run(os.environ["DISCORD_TOKEN"])
