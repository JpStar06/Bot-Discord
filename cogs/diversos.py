import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class Duversos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @bot.event()
    Async await 


async def setup(bot):
    await bot.add_cog(Mods(bot))