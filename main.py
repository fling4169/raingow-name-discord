import os
import threading
from flask import Flask
from rainbow_bot import RainbowBot

ROLE_ID = 1376734144658407555  # Replace with your role ID

# Bot tokens from env
TOKENS = [
    os.environ.get("DISCORD_TOKEN_1"),
    os.environ.get("DISCORD_TOKEN_2"),
    os.environ.get("DISCORD_TOKEN_3"),
    os.environ.get("DISCORD_TOKEN_4"),
    os.environ.get("DISCORD_TOKEN_5")
]

# Flask server for uptime
app = Flask(__name__)

@app.route("/")
def index():
    return "🌈 Multi-Bot Rainbow Role is online!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Start bots
for i, token in enumerate(TOKENS):
    if token:
        bot = RainbowBot(token, ROLE_ID, offset_seconds=i)
        threading.Thread(target=bot.run_bot).start()

# Start Flask server last
threading.Thread(target=run_flask).start()
