import os
import threading
from flask import Flask
from rainbow_bot import RainbowBot

ROLE_ID = 1376734144658407555  # Replace with your actual role ID

TOKENS = [
    os.environ.get("DISCORD_TOKEN_1"),
    os.environ.get("DISCORD_TOKEN_2"),
    os.environ.get("DISCORD_TOKEN_3"),
    os.environ.get("DISCORD_TOKEN_4"),
    os.environ.get("DISCORD_TOKEN_5"),
]

app = Flask(__name__)

@app.route("/")
def index():
    return "🌈 Multi-Bot Rainbow Role is online!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

base_interval = 5  # Base seconds between updates

for i, token in enumerate(TOKENS):
    if token:
        update_interval = base_interval + i  # e.g. 5s, 6s, 7s, ...
        bot = RainbowBot(token, ROLE_ID, update_interval=update_interval)
        threading.Thread(target=bot.run_bot).start()

threading.Thread(target=run_flask).start()
