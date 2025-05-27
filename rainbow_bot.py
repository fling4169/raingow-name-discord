import discord
from discord.ext import commands, tasks
import colorsys

class RainbowBot(commands.Bot):
    def __init__(self, role_id, update_interval=5):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        self.role_id = role_id
        self.update_interval = update_interval
        self.color_index = 0
        self.change_color_loop = tasks.loop(seconds=self.update_interval)(self.change_color)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        if not self.change_color_loop.is_running():
            self.change_color_loop.start()

    async def change_color(self):
        if not self.guilds:
            return

        guild = self.guilds[0]
        role = guild.get_role(self.role_id)
        if role is None:
            print(f"Role ID {self.role_id} not found in guild {guild.name}")
            return

        hue = (self.color_index % 360) / 360.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
        color = discord.Color.from_rgb(int(r * 255), int(g * 255), int(b * 255))

        try:
            await role.edit(color=color, reason="Rainbow role color update")
        except discord.Forbidden:
            print("Missing permissions to edit the role.")
        except discord.HTTPException as e:
            print(f"Failed to update role color: {e}")

        self.color_index += 1

def create_bot(token, role_id, update_interval):
    bot = RainbowBot(role_id=role_id, update_interval=update_interval)
    return bot
