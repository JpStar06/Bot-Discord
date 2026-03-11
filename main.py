import discord
from discord.ext import commands
import json
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

with open("config.json", "r") as f:
    config = json.load(f)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logado como {bot.user}")

async def main():
    async with bot:
        await bot.load_extension("cogs.comandos")
        await bot.load_extension("cogs.tickets")
        await bot.start(config["token"])

asyncio.run(main())