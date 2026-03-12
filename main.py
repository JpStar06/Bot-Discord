import discord
from discord.ext import commands
import os

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logado como {bot.user}")

async def load_cogs():
    for root, dirs, files in os.walk("./cogs"):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                module = path.replace("/", ".").replace("\\", ".")[:-3]
                await bot.load_extension(module)

async def main():
    async with bot:
        await load_cogs()
        await bot.start("TOKEN")

import asyncio
asyncio.run(main())