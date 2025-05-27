import discord
from discord.ext import commands, tasks
import itertools
from flask import Flask
import threading
import os

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Rainbow color cycle
rainbow_colors = itertools.cycle([
    discord.Color.red(),
    discord.Color.orange(),
    discord.Color.gold(),
    discord.Color.green(),
    discord.Color.blue(),
    discord.Color.purple()
])

ROLE_NAME = "Rainbow"  # Change this if needed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    change_color.start()

@tasks.loop(seconds=5)
async def change_color():
    for guild in bot.guilds:
        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if role:
            try:
                await role.edit(color=next(rainbow_colors))
            except discord.Forbidden:
                print(f"Missing permissions to edit role '{ROLE_NAME}' in {guild.name}")

# Flask web server for uptime pings
app = Flask("")

@app.route("/")
def home():
    return "Rainbow Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def start_flask():
    thread = threading.Thread(target=run_flask)
    thread.start()

# Start Flask then run bot
start_flask()
bot.run(os.environ["DISCORD_TOKEN"])
