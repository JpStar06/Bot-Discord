import discord
from discord.ext import commands
import asyncio
import os
import dotenv

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logado como {bot.user}")
    await bot.tree.sync()


async def main():
    async with bot:
        await bot.load_extension("cogs.comandos")
        await bot.load_extension("cogs.tickets")
        await bot.load_extension("cogs.comandos_mod")
        await bot.start(TOKEN)


asyncio.run(main())