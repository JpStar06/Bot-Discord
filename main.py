import discord
from discord.ext import commands
import os
import dotenv
from database import setup_database
import asyncio

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

async def load_cogs():
    for folder in os.listdir("./cogs"):
        for file in os.listdir(f"./cogs/{folder}"):
            if file.endswith(".py") and file != "__init__.py":
                await bot.load_extension(f"cogs.{folder}.{file[:-3]}")

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")
    setup_database()

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())