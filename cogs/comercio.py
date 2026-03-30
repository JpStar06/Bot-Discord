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

    async def get_conn(self):
        pool = await get_connection()
        return pool.acquire()

    async def get_user(self, user_id):
        async with await self.get_conn() as conn:

            user = await conn.fetchrow(
                "SELECT coins, daily_streak, last_daily FROM economy WHERE user_id=$1",
                user_id
            )

            if not user:
                await conn.execute(
                    "INSERT INTO economy (user_id, coins, daily_streak) VALUES ($1,0,0)",
                    user_id
                )
                return 0, 0, None

            return user["coins"], user["daily_streak"], user["last_daily"]

    async def update_user(self, user_id, coins=None, streak=None, last=None):
        async with await self.get_conn() as conn:

            await conn.execute("""
                UPDATE economy
                SET coins = COALESCE($1, coins),
                    daily_streak = COALESCE($2, daily_streak),
                    last_daily = COALESCE($3, last_daily)
                WHERE user_id = $4
            """, coins, streak, last, user_id)

    async def add_coins(self, user_id, amount):
        async with await self.get_conn() as conn:
            await conn.execute(
                "UPDATE economy SET coins = coins + $1 WHERE user_id=$2",
                amount, user_id
            )

    # ================= INVENTÁRIO =================

    async def add_item(self, user_id, item_id, qtd):
        async with await self.get_conn() as conn:
            await conn.execute("""
                INSERT INTO members_inventory (user_id, item_id, quantidade)
                VALUES ($1,$2,$3)
                ON CONFLICT (user_id, item_id)
                DO UPDATE SET quantidade = members_inventory.quantidade + $3
            """, user_id, item_id, qtd)

    async def remove_item(self, user_id, item_id, qtd):
        async with await self.get_conn() as conn:

            item = await conn.fetchrow("""
                SELECT quantidade FROM members_inventory
                WHERE user_id=$1 AND item_id=$2
            """, user_id, item_id)

            if not item or item["quantidade"] < qtd:
                return False

            await conn.execute("""
                UPDATE members_inventory
                SET quantidade = quantidade - $1
                WHERE user_id=$2 AND item_id=$3
            """, qtd, user_id, item_id)

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
            f"💰 **{coins} coins**\n🔥 Streak: {streak}"
        )

    @economia.command(name="daily")
    async def daily(self, interaction: discord.Interaction):

        coins, streak, last = await self.get_user(interaction.user.id)

        today = int(datetime.datetime.utcnow().strftime("%Y%m%d"))

        if last == today:
            await interaction.response.send_message("⏳ Já pegou hoje.", ephemeral=True)
            return

        streak += 1
        reward = random.randint(100, 500) + (streak * 20)

        await self.update_user(
            interaction.user.id,
            coins=coins + reward,
            streak=streak,
            last=today
        )

        await interaction.response.send_message(
            f"🎁 +{reward} coins\n🔥 streak: {streak}"
        )

    @economia.command(name="work")
    @app_commands.checks.cooldown(1, 600)
    async def work(self, interaction: discord.Interaction):

        job = random.choice(["programador", "minerador", "chef", "hacker", "músico"])
        reward = random.randint(100, 400)

        await self.add_coins(interaction.user.id, reward)

        await interaction.response.send_message(
            f"💼 Trabalhou como **{job}** e ganhou {reward}"
        )

    @economia.command(name="rank")
    async def rank(self, interaction: discord.Interaction):

        async with await self.get_conn() as conn:
            users = await conn.fetch(
                "SELECT user_id, coins FROM economy ORDER BY coins DESC LIMIT 10"
            )

        text = ""

        for i, u in enumerate(users, 1):
            try:
                user = await self.bot.fetch_user(u["user_id"])
                name = user.name
            except:
                name = "Desconhecido"

            text += f"{i}. {name} — {u['coins']}\n"

        await interaction.response.send_message(f"🏆 Ranking:\n{text}")

    # ================= LOOTBOX =================

    @box.command(name="comprar")
    async def comprar(self, interaction: discord.Interaction):

        coins, _, _ = await self.get_user(interaction.user.id)

        if coins < 500:
            await interaction.response.send_message("💸 Sem coins.", ephemeral=True)
            return

        await self.add_coins(interaction.user.id, -500)

        box = random.choices(
            ["comum", "raro", "epico", "lendario", "mitico"],
            weights=[60, 25, 10, 4, 1]
        )[0]

        await self.add_item(interaction.user.id, f"box_{box}", 1)

        await interaction.response.send_message(f"📦 Box **{box}** obtida!")

    @box.command(name="abrir")
    async def abrir(self, interaction: discord.Interaction, box_id: str):

        if not await self.remove_item(interaction.user.id, box_id, 1):
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

        await interaction.response.send_message(f"🎁 +{reward} coins")

    # ================= INVENTÁRIO =================

    @economia.command(name="inventario")
    async def inventario(self, interaction: discord.Interaction):

        async with await self.get_conn() as conn:
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
    async def vender(self, interaction: discord.Interaction, item_id: str, qtd: int, preco: int):

        if not await self.remove_item(interaction.user.id, item_id, qtd):
            await interaction.response.send_message("❌ você não tem isso")
            return

        async with await self.get_conn() as conn:
            await conn.execute("""
                INSERT INTO marketplace (seller_id, item_id, quantidade, preco)
                VALUES ($1,$2,$3,$4)
            """, interaction.user.id, item_id, qtd, preco)

        await interaction.response.send_message("🛒 listado")

    @economia.command(name="mercado")
    async def mercado(self, interaction: discord.Interaction):

        async with await self.get_conn() as conn:
            items = await conn.fetch("SELECT * FROM marketplace LIMIT 10")

        if not items:
            await interaction.response.send_message("🛒 vazio")
            return

        text = "\n".join([
            f"ID {i['listing_id']} • {i['item_id']} x{i['quantidade']} — {i['preco']}"
            for i in items
        ])

        await interaction.response.send_message(text)


async def setup(bot):
    await bot.add_cog(Economia(bot))
