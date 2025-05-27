# Optional utility file
import discord
import colorsys

def generate_rainbow_colors(n=100):
    return [
        discord.Color.from_rgb(*[int(c * 255) for c in colorsys.hsv_to_rgb(i / n, 1, 1)])
        for i in range(n)
    ]
