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
        reward = random.randint(100, 400)

        await self.add_coins(interaction.user.id, reward)

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

        if not users:
            await interaction.response.send_message("Nenhum dado no ranking.")
            return

        text = ""
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
        embed = discord.Embed(
            title = '**🎉PARABÉNS🎉**',
            description = f"📦 Lootbox aberta!\n{rarity}\nVocê ganhou **{reward} coins**",
            color = discord.Color.green()
        )
        await interaction.response.send_message(embed = embed)

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

async def setup(bot):
    await bot.add_cog(Economia(bot))
