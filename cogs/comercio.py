import discord
from discord.ext import commands
from discord import app_commands
import time

from database import get_connection


class Comercio(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def get_user(self, user_id):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM economy WHERE user_id = ?",
            (user_id,)
        )

        user = cursor.fetchone()

        if not user:
            cursor.execute(
                "INSERT INTO economy (user_id, coins, last_daily) VALUES (?,0,0)",
                (user_id,)
            )
            conn.commit()

        conn.close()


    def get_coins(self, user_id):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT coins FROM economy WHERE user_id = ?",
            (user_id,)
        )

        result = cursor.fetchone()
        conn.close()

        return result[0]


    @app_commands.command(name="saldo", description="Ver suas Aiko Coins")
    async def saldo(self, interaction: discord.Interaction):

        user_id = interaction.user.id

        self.get_user(user_id)
        coins = self.get_coins(user_id)

        await interaction.response.send_message(
            f"💰 Você tem **{coins} Aiko Coins**"
        )


    @app_commands.command(name="aikodaily", description="Recompensa diária")
    async def daily(self, interaction: discord.Interaction):

        user_id = interaction.user.id
        self.get_user(user_id)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT last_daily FROM economy WHERE user_id = ?",
            (user_id,)
        )

        last_daily = cursor.fetchone()[0]
        now = int(time.time())

        if now - last_daily < 86400:

            await interaction.response.send_message(
                "⏳ Você já pegou sua recompensa hoje."
            )

            conn.close()
            return


        reward = 100

        cursor.execute(
            """
            UPDATE economy
            SET coins = coins + ?, last_daily = ?
            WHERE user_id = ?
            """,
            (reward, now, user_id)
        )

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"🎉 Você recebeu **{reward} Aiko Coins**!"
        )

async def setup(bot):
    await bot.add_cog(Comercio(bot))