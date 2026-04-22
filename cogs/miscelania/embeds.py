import discord

def ball(msg: str):
    return discord.Embed(
        title="🎱 **8Ball**",
        description=msg,
        color=discord.Color.dark_grey()
    )