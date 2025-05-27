import os
from multiprocessing import Process
from flask import Flask
from rainbow_bot import RainbowBot

ROLE_ID = 1376734144658407555  # Replace with your role ID

TOKENS = [
    os.environ.get("DISCORD_TOKEN_1"),
    os.environ.get("DISCORD_TOKEN_2"),
    os.environ.get("DISCORD_TOKEN_3"),
    os.environ.get("DISCORD_TOKEN_4"),
    os.environ.get("DISCORD_TOKEN_5")
]

app = Flask(__name__)

@app.route("/")
def index():
    return "🌈 Multi-Bot Rainbow Role is online!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def run_bot_process(token, role_id, offset_seconds):
    bot = RainbowBot(token, role_id, offset_seconds)
    bot.run_bot()

if __name__ == "__main__":
    # Start the Flask server in a separate process
    flask_process = Process(target=run_flask)
    flask_process.start()

    # Start each bot in its own process
    processes = []
    for i, token in enumerate(TOKENS):
        if token:
            p = Process(target=run_bot_process, args=(token, ROLE_ID, i))
            p.start()
            processes.append(p)

    # Optionally join processes if you want the main process to wait
    for p in processes:
        p.join()
    flask_process.join()
