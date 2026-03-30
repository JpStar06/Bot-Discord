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

    # ================= DATABASE =================

    async def get_user(self, user_id):
        pool = await get_connection()

        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT coins, daily_streak, last_daily FROM economy WHERE user_id=$1",
                user_id
            )

            if not result:
                await conn.execute(
                    "INSERT INTO economy (user_id, coins, daily_streak) VALUES ($1,$2,$3)",
                    user_id, 0, 0
                )
                return (0, 0, None)

            return (
                result["coins"],
                result["daily_streak"],
                result["last_daily"]
            )

    async def add_coins(self, user_id, amount):
        pool = await get_connection()

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE economy SET coins = coins + $1 WHERE user_id=$2",
                amount, user_id
            )

    # ================= INVENTÁRIO =================

    async def add_item(self, user_id, item_id, quantidade):
        pool = await get_connection()

        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO members_inventory (user_id, item_id, quantidade)
                VALUES ($1,$2,$3)
                ON CONFLICT (user_id, item_id)
                DO UPDATE SET quantidade = members_inventory.quantidade + $3
            """, user_id, item_id, quantidade)

    async def remove_item(self, user_id, item_id, quantidade):
        pool = await get_connection()

        async with pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT quantidade FROM members_inventory
                WHERE user_id=$1 AND item_id=$2
            """, user_id, item_id)

            if not result or result["quantidade"] < quantidade:
                return False

            await conn.execute("""
                UPDATE members_inventory
                SET quantidade = quantidade - $1
                WHERE user_id=$2 AND item_id=$3
            """, quantidade, user_id, item_id)

            await conn.execute("""
                DELETE FROM members_inventory
                WHERE user_id=$1 AND item_id=$2 AND quantidade <= 0
            """, user_id, item_id)

            return True

    # ================= ECONOMIA =================

    @economia.command(name="coins")
    async def coins(self, interaction: discord.Interaction):

        coins, streak, _ = await self.get_user(interaction.user.id)

        await interaction.response.send_message(
            f"💰 Coins: **{coins}**\n🔥 Streak: **{streak}**"
        )

    @economia.command(name="daily")
    async def daily(self, interaction: discord.Interaction):

        coins, streak, last = await self.get_user(interaction.user.id)

        now = int(datetime.datetime.utcnow().strftime("%Y%m%d"))

        if last == now:
            await interaction.response.send_message("⏳ Já coletou hoje.", ephemeral=True)
            return

        streak += 1
        reward = random.randint(100, 500) + (streak * 20)

        pool = await get_connection()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE economy SET coins=$1, daily_streak=$2, last_daily=$3 WHERE user_id=$4",
                coins + reward, streak, now, interaction.user.id
            )

        await interaction.response.send_message(
            f"🎁 +{reward} coins | 🔥 streak {streak}"
        )

    @economia.command(name="work")
    @app_commands.checks.cooldown(1, 600)
    async def work(self, interaction: discord.Interaction):

        jobs = ["programador", "minerador", "chef", "hacker", "músico"]
        job = random.choice(jobs)
        reward = random.randint(100, 400)

        await self.add_coins(interaction.user.id, reward)

        await interaction.response.send_message(
            f"💼 Você trabalhou como **{job}** e ganhou {reward}"
        )

    @economia.command(name="rank")
    async def rank(self, interaction: discord.Interaction):

        pool = await get_connection()
        async with pool.acquire() as conn:
            users = await conn.fetch(
                "SELECT user_id, coins FROM economy ORDER BY coins DESC LIMIT 10"
            )

        text = ""
        for i, u in enumerate(users, start=1):
            user = await self.bot.fetch_user(int(u["user_id"]))
            text += f"{i}. {user.name} — {u['coins']}\n"

        await interaction.response.send_message(f"🏆 Ranking:\n{text}")

    # ================= LOOTBOX =================

    @box.command(name="comprar")
    async def buy_box(self, interaction: discord.Interaction):

        price = 500
        coins, _, _ = await self.get_user(interaction.user.id)

        if coins < price:
            await interaction.response.send_message("💸 Sem coins.", ephemeral=True)
            return

        await self.add_coins(interaction.user.id, -price)

        box_types = ["comum", "raro", "epico", "lendario", "mitico"]
        weights = [60, 25, 10, 4, 1]

        box = random.choices(box_types, weights=weights)[0]

        await self.add_item(interaction.user.id, f"box_{box}", 1)

        await interaction.response.send_message(f"📦 Você ganhou uma box **{box}**")

    @box.command(name="abrir")
    async def open_box(self, interaction: discord.Interaction, box_id: str):

        ok = await self.remove_item(interaction.user.id, box_id, 1)

        if not ok:
            await interaction.response.send_message("❌ Você não tem essa box.", ephemeral=True)
            return

        rewards = {
            "box_comum": random.randint(400, 500),
            "box_raro": random.randint(500, 700),
            "box_epico": random.randint(700, 900),
            "box_lendario": random.randint(1000, 2000),
            "box_mitico": None
        }

        reward = rewards.get(box_id)

        coins, _, _ = await self.get_user(interaction.user.id)

        if reward is None:
            reward = coins * 2

        await self.add_coins(interaction.user.id, reward)

        await interaction.response.send_message(
            f"🎁 Você ganhou **{reward} coins**"
        )

    # ================= INVENTÁRIO =================

    @economia.command(name="inventario")
    async def inventario(self, interaction: discord.Interaction):

        pool = await get_connection()

        async with pool.acquire() as conn:
            items = await conn.fetch(
                "SELECT item_id, quantidade FROM members_inventory WHERE user_id=$1",
                interaction.user.id
            )

        if not items:
            await interaction.response.send_message("📦 vazio")
            return

        text = "\n".join([f"{i['item_id']} x{i['quantidade']}" for i in items])

        await interaction.response.send_message(f"🎒\n{text}")

    # ================= MERCADO =================

    @economia.command(name="vender")
    async def vender(self, interaction: discord.Interaction, item_id: str, quantidade: int, preco: int):

        ok = await self.remove_item(interaction.user.id, item_id, quantidade)

        if not ok:
            await interaction.response.send_message("❌ você não tem isso")
            return

        pool = await get_connection()

        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO marketplace (seller_id, item_id, quantidade, preco)
                VALUES ($1,$2,$3,$4)
            """, interaction.user.id, item_id, quantidade, preco)

        await interaction.response.send_message("🛒 listado")

    @economia.command(name="mercado")
    async def mercado(self, interaction: discord.Interaction):

        pool = await get_connection()

        async with pool.acquire() as conn:
            items = await conn.fetch("SELECT * FROM marketplace LIMIT 10")

        if not items:
            await interaction.response.send_message("🛒 vazio")
            return

        text = ""

        for i in items:
            text += f"ID {i['listing_id']} • {i['item_id']} x{i['quantidade']} — {i['preco']}\n"

        await interaction.response.send_message(text)


async def setup(bot):
    await bot.add_cog(Economia(bot))
