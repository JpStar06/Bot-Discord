# cogs/economia.py
import discord
from discord import app_commands
from discord.ext import commands
import random
import datetime
from database import get_connection

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None

    async def cog_load(self):
        self.pool = await get_connection()  # Pool asyncpg

    economia = app_commands.Group(name="eco", description="Sistema de economia")
    box = app_commands.Group(name="box", description="Sistema de lootbox")

<<<<<<< Updated upstream
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
=======
    # -------------------- PEGAR USUÁRIO --------------------
    async def get_user(self, user_id):
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT coins, daily_streak, last_daily, boxes FROM economy WHERE user_id=$1", user_id)
            if not user:
                await conn.execute(
                    "INSERT INTO economy (user_id, coins, daily_streak, boxes) VALUES ($1, $2, $3, $4)",
                    user_id, 0, 0, 0
                )
                return {"coins": 0, "daily_streak": 0, "last_daily": None, "boxes": 0}
            return user

    async def add_coins(self, user_id, amount):
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE economy SET coins = coins + $1 WHERE user_id=$2", amount, user_id)

    # -------------------- COINS --------------------
    @economia.command(name="carteira", description="Ver suas coins")
    async def coins(self, interaction: discord.Interaction):
        user = await self.get_user(interaction.user.id)
        embed = discord.Embed(
            title="💰 Carteira",
            description=f"Coins: **{user['coins']}**\nDaily streak: **{user['daily_streak']}**",
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed)

    # -------------------- DAILY --------------------
    @economia.command(name="daily", description="Pegue coins diárias")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user = await self.get_user(interaction.user.id)

        now = int(datetime.datetime.utcnow().strftime("%Y%m%d"))

        if user['last_daily'] == now:
            await interaction.followup.send("⏳ Você já pegou o daily hoje.", ephemeral=True)
            return

        streak = user['daily_streak'] or 0
        streak += 1
        reward = random.randint(100, 500) + (streak * 20)

        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE economy SET coins=coins+$1, daily_streak=$2, last_daily=$3 WHERE user_id=$4",
                reward, streak, now, interaction.user.id
            )

        await interaction.followup.send(f"🎁 Daily coletado!\n+{reward} coins\n🔥 Streak: {streak}")

    # -------------------- WORK --------------------
    @economia.command(name="work", description="Trabalhe para ganhar coins")
    @app_commands.checks.cooldown(8, 600)
    async def work(self, interaction: discord.Interaction):
        jobs = ["programador", "minerador", "chef", "hacker", "músico"]
        job = random.choice(jobs)
>>>>>>> Stashed changes
        reward = random.randint(100, 400)

        await self.add_coins(interaction.user.id, reward)

<<<<<<< Updated upstream
        await interaction.response.send_message(
            f"💼 Trabalhou como **{job}** e ganhou {reward}"
        )

    @economia.command(name="rank")
    async def rank(self, interaction: discord.Interaction):

        async with await self.get_conn() as conn:
            users = await conn.fetch(
                "SELECT user_id, coins FROM economy ORDER BY coins DESC LIMIT 10"
            )
=======
        embed = discord.Embed(
            title="💼 WORK",
            description=f"Você trabalhou como **{job}** por 1 hora\n💰 Recebeu **{reward} coins**",
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed)
    # -------------------- RANKING --------------------
    @economia.command(name="rank", description="Ranking de coins")
    async def rank(self, interaction: discord.Interaction):
        async with self.pool.acquire() as conn:
            users = await conn.fetch("SELECT user_id, coins FROM economy ORDER BY coins DESC LIMIT 10")
>>>>>>> Stashed changes

        text = ""
<<<<<<< Updated upstream

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

=======
        for i, u in enumerate(users, start=1):
            try:
                user_obj = self.bot.get_user(int(u['user_id'])) or await self.bot.fetch_user(int(u['user_id']))
                text += f"{i}. {user_obj.name} — {u['coins']} coins\n"
            except:
                continue

        embed = discord.Embed(title="🏆 Ranking", description=text, color=0xf1c40f)
        await interaction.response.send_message(embed=embed)

    # -------------------- COMPRAR BOX --------------------
    @box.command(name="comprar", description="Comprar lootbox")
    async def buy_box(self, interaction: discord.Interaction):
        price = 500
        user = await self.get_user(interaction.user.id)

        if user['coins'] < price:
            faltante = price - user['coins']

            nocoin = discord.Embed(
                title="Saldo insuficiente",
                description=f"💸 Você não possui coins suficientes.\nVocê precisa de mais {faltante} coins para comprar isso.",
                color=discord.Color.red()
            )

            await interaction.response.send_message(embed=nocoin, ephemeral=True)
            return
            
        await self.add_coins(interaction.user.id, -price)
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE economy SET boxes = boxes + 1 WHERE user_id=$1", interaction.user.id)
            buy_box= discord.Embed(
            title = "**Compra**",
            description= "📦 Você comprou uma lootbox!",
            color = discord.Color.green()
            )
            await interaction.response.send_message(embed=buy_box)

    # -------------------- ABRIR BOX --------------------
    @box.command(name="abrir", description="Abrir lootbox")
    async def open_box(self, interaction: discord.Interaction):
        user = await self.get_user(interaction.user.id)

        if not user or user['boxes'] <= 0:
            await interaction.response.send_message("📦 Você não tem lootboxes.", ephemeral=True)
            return

        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE economy SET boxes = boxes - 1 WHERE user_id=$1", interaction.user.id)

        rewards = [
            (random.randint(400, 500), "🪙 comum"),
            (random.randint(500, 700), "✨ raro"),
            (random.randint(700, 900), "💎 épico"),
            (random.randint(1000, 3000), "👑 lendário"),
            (user['coins'] * 2, "🌟 mítico")
        ]
        reward, rarity = random.choices(rewards, weights=[60,25,10,5,1])[0]
        await self.add_coins(interaction.user.id, reward)

        await interaction.response.send_message(f"📦 Lootbox aberta!\n{rarity}\nVocê ganhou **{reward} coins**")

    # -------------------- PAY --------------------
    @economia.command(name="pay", description="Envie coins para outro usuário")
    async def pay(self, interaction: discord.Interaction, usuario: discord.Member, quantia: int):
        if usuario.id == interaction.user.id:
            await interaction.response.send_message("❌ Você não pode pagar a si mesmo.", ephemeral=True)
            return
        if quantia <= 0:
            await interaction.response.send_message("❌ Quantia inválida.", ephemeral=True)
            return

        user = await self.get_user(interaction.user.id)
        if quantia > user['coins']:
            await interaction.response.send_message("❌ Você não tem coins suficientes.", ephemeral=True)
            return

        taxa = int(quantia * 0.05)
        recebido = quantia - taxa

        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE economy SET coins = coins - $1 WHERE user_id=$2", quantia, interaction.user.id)
            await conn.execute("INSERT INTO economy (user_id, coins) VALUES ($1, 0) ON CONFLICT (user_id) DO NOTHING", usuario.id)
            await conn.execute("UPDATE economy SET coins = coins + $1 WHERE user_id=$2", recebido, usuario.id)

        embed = discord.Embed(
            title="💸 Transferência",
            description=(
                f"{interaction.user.mention} enviou **{recebido} coins** para {usuario.mention}\n\n"
                f"💰 Valor enviado: `{quantia}`\n"
                f"🏦 Taxa: `{taxa}` (5%)"
            ),
            color=0x2ecc71
        )
        await interaction.response.send_message(embed=embed)

    # -------------------- LOJA --------------------
    @economia.command(name="lojinha", description="Veja a loja diária")
    async def shop(self, interaction: discord.Interaction):
        today = int(datetime.datetime.utcnow().strftime("%Y%m%d"))
        random.seed(today)

        items = [
            ("📦 Lootbox", 500),
            ("🎰 Ticket de cassino", 300),
            ("💎 Gem misteriosa", 1200),
            ("🍀 Amuleto da sorte", 800),
            ("🎨 Cor exclusiva", 2000),
            ("⚡ Boost de trabalho", 1000)
        ]
        shop_items = random.sample(items, 3)
        text = "".join([f"{i+1}. {item[0]} — `{item[1]} coins`\n" for i, item in enumerate(shop_items)])

        embed = discord.Embed(title="🛒 Loja diária", description=text, color=0x3498db)
        await interaction.response.send_message(embed=embed)

    # -------------------- ERROS --------------------
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            segundos = int(error.retry_after)
            minutos, segundos = divmod(segundos, 60)
            await interaction.response.send_message(
                f"Você está trabalhando muito.\nTente novamente em **{minutos}m {segundos}s**.",
                ephemeral=True
            )
>>>>>>> Stashed changes

async def setup(bot):
    await bot.add_cog(Economia(bot))
