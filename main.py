<<<<<<< Updated upstream
import discord
from discord.ext import commands
import asyncio
import os
import dotenv
from database import init_db

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    if not hasattr(bot, "db_initialized"):
        await init_db()
        bot.db_initialized = True
        print("✅ Banco iniciado")

    await bot.tree.sync()
    print(f"Logado como {bot.user}")
    
async def main():
    async with bot:
        await bot.load_extension("cogs.tickets")
        await bot.load_extension("cogs.comandos_mod")
        await bot.load_extension("cogs.Misc")
        await bot.load_extension("cogs.comercio")
        await bot.load_extension("cogs.reminders")
        await bot.load_extension("cogs.casino")
        await bot.load_extension("cogs.embeds")
        await bot.start(TOKEN)


asyncio.run(main())
=======
import discord
from discord.ext import commands
import asyncio
import os
import dotenv
from database import init_db

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logado como {bot.user}")
    await bot.tree.sync()


async def main():
    await init_db()  # 🔥 INICIA O BANCO ANTES DAS COGS

    async with bot:
        await bot.load_extension("cogs.comandos")
        await bot.load_extension("cogs.tickets")
        await bot.load_extension("cogs.comandos_mod")
        await bot.load_extension("cogs.Misc")
        await bot.load_extension("cogs.comercio")
        await bot.load_extension("cogs.reminders")
        await bot.load_extension("cogs.casino")

        await bot.start(TOKEN)


asyncio.run(main())
asyncio.run(main())
>>>>>>> Stashed changes
