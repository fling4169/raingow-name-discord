import discord
import asyncio
import os
from itertools import cycle
from dotenv import load_dotenv

load_dotenv()

# Environment variables for bot tokens
TOKENS = [
    os.getenv("DISCORD_TOKEN_1"),
    os.getenv("DISCORD_TOKEN_2"),
    os.getenv("DISCORD_TOKEN_3"),
    os.getenv("DISCORD_TOKEN_4"),
    os.getenv("DISCORD_TOKEN_5"),
]

GUILD_ID = int(os.getenv("GUILD_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))

# Colors to cycle through (add more if needed)
colors = cycle([
    discord.Colour.red(),
    discord.Colour.green(),
    discord.Colour.blue(),
    discord.Colour.orange(),
    discord.Colour.purple()
])

async def run_bot(token, delay_offset):
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        print(f'{bot.user} has connected.')
        await asyncio.sleep(delay_offset)  # Offset each bot's timer

        while True:
            try:
                guild = bot.get_guild(GUILD_ID)
                role = guild.get_role(ROLE_ID)
                new_color = next(colors)
                await role.edit(colour=new_color, reason="Cycling role color")
                print(f"{bot.user} changed color to {new_color}")
                await asyncio.sleep(10)  # Wait before next change
            except Exception as e:
                print(f"Error with {bot.user}: {e}")
                await asyncio.sleep(10)

    await bot.start(token)

async def main():
    tasks = [
        run_bot(TOKENS[i], delay_offset=i * 2)  # Offset each bot by 2 seconds
        for i in range(len(TOKENS))
    ]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
