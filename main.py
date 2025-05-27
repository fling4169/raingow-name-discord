import os
import threading
import asyncio
from flask import Flask
from rainbow_bot import create_bot

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

def run_bot_instance(token, role_id, update_interval):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = create_bot(token, role_id, update_interval)
    loop.run_until_complete(bot.start(token))

# Start each bot in its own thread
base_interval = 5
for i, token in enumerate(TOKENS):
    if token:
        update_interval = base_interval + i  # e.g. 5s, 6s, ...
        threading.Thread(target=run_bot_instance, args=(token, ROLE_ID, update_interval)).start()

# Run Flask app in its own thread
