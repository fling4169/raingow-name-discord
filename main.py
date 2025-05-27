import os
import time
import threading
import socket
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

def start_bot_with_retry(token, role_id, interval, max_retries=5):
    attempt = 0
    while attempt < max_retries:
        try:
            bot = RainbowBot(token, role_id, update_interval=interval)
            print(f"[INFO] Starting bot with interval {interval}s (Attempt {attempt + 1})...")
            bot.run_bot()
            break  # Exit loop if successful
        except socket.gaierror as e:
            print(f"[ERROR] DNS resolution failed (Attempt {attempt + 1}): {e}")
            attempt += 1
            time.sleep(5)
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            break  # Don't retry for unknown exceptions

def launch_bots():
    print("[INFO] Waiting 5 seconds before launching bots...")
    time.sleep(5)

    base_interval = 5  # Base seconds between role updates

    for i, token in enumerate(TOKENS):
        if not token:
            print(f"[WARN] Token {i + 1} is missing, skipping this bot.")
            continue

        interval = base_interval + i
        delay = i * 3  # Stagger launch to avoid DNS congestion

        def delayed_start(token=token, interval=interval):
            print(f"[INFO] Launching bot {i + 1} after {delay} seconds...")
            time.sleep(delay)
            start_bot_with_retry(token, ROLE_ID, interval)

        threading.Thread(target=delayed_start).start()

threading.Thread(target=run_flask).start()
launch_bots()
