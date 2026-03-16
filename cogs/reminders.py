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

        agora = datetime.datetime.now(
             ZoneInfo("America/Sao_Paulo"
        )).strftime("%H:%M")

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT guild_id, channel_id, embed_id
        FROM reminders
        WHERE horario=%s
        """, (agora,))

        reminders = cursor.fetchall()

        for guild_id, channel_id, embed_id in reminders:

            cursor.execute("""
            SELECT title, description, color, image
            FROM embeds
            WHERE id=%s AND guild_id=%s
            """, (embed_id, guild_id))

            embed_data = cursor.fetchone()

            if not embed_data:
                continue

            title, description, color, image = embed_data

            embed = discord.Embed(
                title=title,
                description=description,
                color=color
            )

            if image:
                embed.set_image(url=image)

            channel = self.bot.get_channel(channel_id)

            if channel:
                try:
                    await channel.send(embed=embed)
                except:
                    pass

        conn.close()


    @check_reminders.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Reminders(bot))