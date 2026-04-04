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
    await init_db()

    async with bot:
        count = 0
        for file in os.listdir("./cogs"):
            if file.endswith(".py") and file != "__init__.py":
                cog_name = file[:-3]  # remove .py
                cog = f"cogs.{cog_name}"

                try:
                    await bot.load_extension(cog)
                    print(f"✅ Cog '{cog_name}' carregada com sucesso!")
                    count += 1
                except Exception as e:
                    print(f"❌ Erro ao carregar '{cog_name}': {e}")
        print(f"\n🚀 Total de cogs carregadas: {count}")

        await bot.start(TOKEN)


asyncio.run(main())
