# cogs/reminders.py
import discord
from discord.ext import commands, tasks
from database import get_connection
import datetime
from zoneinfo import ZoneInfo

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    @tasks.loop(minutes=1)
    async def check_reminders(self):
        # hora atual no fuso de São Paulo
        agora = datetime.datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H:%M")

        async with get_connection().acquire() as conn:
            reminders = await conn.fetch(
                "SELECT guild_id, channel_id, embed_id FROM reminders WHERE horario=$1",
                agora
            )

            for reminder in reminders:
                guild_id = reminder["guild_id"]
                channel_id = reminder["channel_id"]
                embed_id = reminder["embed_id"]

                embed_data = await conn.fetchrow(
                    "SELECT title, description, color, image FROM embeds WHERE id=$1 AND guild_id=$2",
                    embed_id, guild_id
                )
                if not embed_data:
                    continue

                embed = discord.Embed(
                    title=embed_data["title"],
                    description=embed_data["description"],
                    color=embed_data["color"]
                )
                if embed_data["image"]:
                    embed.set_image(url=embed_data["image"])

                channel = self.bot.get_channel(channel_id)
                if channel and channel.permissions_for(channel.guild.me).send_messages:
                    try:
                        await channel.send(embed=embed)
                    except Exception as e:
                        print(f"Erro ao enviar recado: {e}")

    @check_reminders.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Reminders(bot))