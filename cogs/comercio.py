import discord
from discord import app_commands
from discord.ext import commands
import random
import datetime
from database import get_connection


class Economia(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    economia = app_commands.Group(name="eco", description="Sistema de economia")
    box = app_commands.Group(name="box", description="Sistema de lootbox")

    # pegar usuário
    def get_user(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT coins, daily_streak, last_daily FROM economy WHERE user_id=%s",
            (user_id,)
        )

        result = cursor.fetchone()

        if not result:
            cursor.execute(
                "INSERT INTO economy (user_id, coins, daily_streak) VALUES (%s,%s,%s)",
                (user_id, 0, 0)
            )
            conn.commit()
            conn.close()
            return (0, 0, None)

        conn.close()
        return result

    def add_coins(self, user_id, amount):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE economy SET coins = coins + %s WHERE user_id=%s",
            (amount, user_id)
        )

        conn.commit()
        conn.close()

    # coins
    @economia.command(name="coins", description="Ver suas coins")
    async def coins(self, interaction: discord.Interaction):

        coins, streak, last = self.get_user(interaction.user.id)

        embed = discord.Embed(
            title="💰 Carteira",
            description=f"Coins: **{coins}**\nDaily streak: **{streak}**",
            color=0x2ecc71
        )

        await interaction.response.send_message(embed=embed)

    # daily
    @economia.command(name="daily", description="Pegue coins diárias")
    async def daily(self, interaction: discord.Interaction):

        await interaction.response.defer()

        coins, streak, last = self.get_user(interaction.user.id)

        now = datetime.datetime.utcnow()

        if last:
            last = datetime.datetime.fromisoformat(str(last))
            diff = now - last

            if diff.total_seconds() < 86400:
                await interaction.followup.send(
                    "⏳ Você já pegou o daily hoje.",
                    ephemeral=True
                )
                return

        streak += 1

        reward = 200 + (streak * 20)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE economy SET coins=coins+%s, daily_streak=%s, last_daily=%s WHERE user_id=%s",
            (reward, streak, now, interaction.user.id)
        )

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"🎁 Daily coletado!\n+{reward} coins\n🔥 Streak: {streak}"
        )

    # work
    @economia.command(name="work", description="Trabalhe para ganhar coins")
    async def work(self, interaction: discord.Interaction):

        jobs = [
            "programador",
            "minerador",
            "chef",
            "hacker",
            "músico"
        ]

        job = random.choice(jobs)

        reward = random.randint(100, 400)

        self.add_coins(interaction.user.id, reward)

        await interaction.response.send_message(
            f"💼 Você trabalhou como **{job}**\n+{reward} coins"
        )

    # ranking
    @economia.command(name="rank", description="Ranking de coins")
    async def rank(self, interaction: discord.Interaction):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id, coins FROM economy ORDER BY coins DESC LIMIT 10"
        )

        users = cursor.fetchall()
        conn.close()

        text = ""

        for i, u in enumerate(users, start=1):

            user = self.bot.get_user(int(u[0]))

            if user:
                text += f"{i}. {user.name} — {u[1]}\n"

        embed = discord.Embed(
            title="🏆 Ranking",
            description=text,
            color=0xf1c40f
        )

        await interaction.response.send_message(embed=embed)

    # comprar box
    @box.command(name="comprar", description="Comprar lootbox")
    async def buy_box(self, interaction: discord.Interaction):

        price = 500

        coins, _, _ = self.get_user(interaction.user.id)

        if coins < price:
            await interaction.response.send_message(
                "💸 Coins insuficientes.",
                ephemeral=True
            )
            return

        self.add_coins(interaction.user.id, -price)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE economy SET boxes = boxes + 1 WHERE user_id=%s",
            (interaction.user.id,)
        )

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            "📦 Você comprou uma lootbox!"
        )

    # abrir box
    @box.command(name="abrir", description="Abrir lootbox")
    async def open_box(self, interaction: discord.Interaction):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT boxes FROM economy WHERE user_id=%s",
            (interaction.user.id,)
        )

        result = cursor.fetchone()

        if not result or result[0] <= 0:
            await interaction.response.send_message(
                "📦 Você não tem lootboxes.",
                ephemeral=True
            )
            return

        cursor.execute(
            "UPDATE economy SET boxes = boxes - 1 WHERE user_id=%s",
            (interaction.user.id,)
        )

        conn.commit()

        rewards = [
            (50, "🪙 comum"),
            (200, "✨ raro"),
            (500, "💎 épico"),
            (2000, "👑 lendário")
        ]

        reward, rarity = random.choices(
            rewards,
            weights=[60, 25, 10, 5]
        )[0]

        cursor.execute(
            "UPDATE economy SET coins = coins + %s WHERE user_id=%s",
            (reward, interaction.user.id)
        )

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"📦 Lootbox aberta!\n{rarity}\nVocê ganhou **{reward} coins**"
        )


async def setup(bot):
    await bot.add_cog(Economia(bot))