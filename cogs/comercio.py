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

    # ================= USUÁRIO =================

    async def get_user(self, user_id):
        pool = await get_connection()

        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                "SELECT coins, daily_streak, last_daily, boxes FROM economy WHERE user_id=$1",
                user_id
            )

            if not result:
                await conn.execute(
                    "INSERT INTO economy (user_id, coins, daily_streak, boxes) VALUES ($1,$2,$3,$4)",
                    user_id, 0, 0, 0
                )
                return (0, 0, None, 0)

            return (
                result["coins"],
                result["daily_streak"],
                result["last_daily"],
                result["boxes"]
            )

    async def add_coins(self, user_id, amount):
        pool = await get_connection()

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE economy SET coins = coins + $1 WHERE user_id=$2",
                amount, user_id
            )

    # ================= COMANDOS =================

<<<<<<< Updated upstream
    def add_item(self, user_id, item_id, quantidade):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO members_inventory (user_id, item_id, quantidade)
            VALUES (%s,%s,%s)
            ON CONFLICT (user_id, item_id)
            DO UPDATE SET quantidade = members_inventory.quantidade + %s
        """, (user_id, item_id, quantidade, quantidade))
        conn.commit()
        conn.close()
    def remove_item(self, user_id, item_id, quantidade):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT quantidade FROM members_inventory
            WHERE user_id=%s AND item_id=%s
        """, (user_id, item_id))
        result = cursor.fetchone()
        if not result or result[0] < quantidade:
            conn.close()
            return False
        cursor.execute("""
            UPDATE members_inventory
            SET quantidade = quantidade - %s
            WHERE user_id=%s AND item_id=%s
        """, (quantidade, user_id, item_id))
        cursor.execute("""
            DELETE FROM members_inventory
            WHERE user_id=%s AND item_id=%s AND quantidade <= 0
        """, (user_id, item_id))
        conn.commit()
        conn.close()
        return True

    # coins
=======
>>>>>>> Stashed changes
    @economia.command(name="coins", description="Ver suas coins")
    async def coins(self, interaction: discord.Interaction):

        coins, streak, last, _ = await self.get_user(interaction.user.id)

        embed = discord.Embed(
            title="💰 Carteira",
            description=f"Coins: **{coins}**\nDaily streak: **{streak}**",
            color=0x2ecc71
        )

        await interaction.response.send_message(embed=embed)

    @economia.command(name="daily", description="Pegue coins diárias")
    async def daily(self, interaction: discord.Interaction):

        await interaction.response.defer()

        coins, streak, last, _ = await self.get_user(interaction.user.id)

        now = int(datetime.datetime.utcnow().strftime("%Y%m%d"))

        if last == now:
            await interaction.followup.send(
                "⏳ Você já pegou o daily hoje.",
                ephemeral=True
            )
            return

        streak = (streak or 0) + 1
        reward = random.randint(100, 500) + (streak * 20)

        pool = await get_connection()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE economy SET coins = coins + $1, daily_streak = $2, last_daily = $3 WHERE user_id = $4",
                reward, streak, now, interaction.user.id
            )

        await interaction.followup.send(
            f"🎁 Daily coletado!\n+{reward} coins\n🔥 Streak: {streak}"
        )

    @economia.command(name="work", description="Trabalhe para ganhar coins")
    @app_commands.checks.cooldown(8, 600)
    async def work(self, interaction: discord.Interaction):

        jobs = ["programador", "minerador", "chef", "hacker", "músico"]

        job = random.choice(jobs)
        reward = random.randint(100, 400)

        await self.add_coins(interaction.user.id, reward)

        await interaction.response.send_message(
            f"💼 Você trabalhou como **{job}** e ganhou {reward} coins"
        )

    @economia.command(name="rank", description="Ranking de coins")
    async def rank(self, interaction: discord.Interaction):

        pool = await get_connection()
        async with pool.acquire() as conn:
            users = await conn.fetch(
                "SELECT user_id, coins FROM economy ORDER BY coins DESC LIMIT 10"
            )

        if not users:
            await interaction.response.send_message("Nenhum dado no ranking.")
            return

        text = ""

        for i, u in enumerate(users, start=1):
            user = self.bot.get_user(int(u["user_id"]))

            if not user:
                try:
                    user = await self.bot.fetch_user(int(u["user_id"]))
                except:
                    continue

            text += f"{i}. {user.name} — {u['coins']} coins\n"

        embed = discord.Embed(
            title="🏆 Ranking",
            description=text,
            color=0xf1c40f
        )

        await interaction.response.send_message(embed=embed)

    # ================= LOOTBOX =================

    @box.command(name="comprar", description="Comprar lootbox")
    async def buy_box(self, interaction: discord.Interaction):

        price = 500
        coins, _, _, boxes = await self.get_user(interaction.user.id)

        if coins < price:
            await interaction.response.send_message(
                "💸 Coins insuficientes.",
                ephemeral=True
            )
            return
        
        boxes = [
            ("box_comum", "🪙 comum"),
            ("box_raro", "✨ raro"),
            ("box_epico", "💎 épico"),
            ("box_lendario", "👑 lendário"),
            ("box_mitico", "🌟 mítico")
        ]

<<<<<<< Updated upstream
        box_id, rarity = random.choices(
        boxes,
        weights=[60, 25, 10, 5, 1]
        )[0]

        # remove coins
        self.add_coins(interaction.user.id, -price)

        # adiciona lootbox ao inventário
        self.add_item(interaction.user.id, box_id, 1)

        await interaction.response.send_message(
            f"📦 Você comprou **1 {box_id}**"
        )

    # abrir box
=======
        pool = await get_connection()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE economy SET coins = coins - $1, boxes = boxes + 1 WHERE user_id=$2",
                price, interaction.user.id
            )

        await interaction.response.send_message("📦 Você comprou uma lootbox!")

>>>>>>> Stashed changes
    @box.command(name="abrir", description="Abrir lootbox")
    async def open_box(self, interaction: discord.Interaction, box_id: str):

<<<<<<< Updated upstream
        # remove box do inventário
        ok = self.remove_item(interaction.user.id, box_id, 1)

        if not ok:
=======
        coins, _, _, boxes = await self.get_user(interaction.user.id)

        if boxes <= 0:
>>>>>>> Stashed changes
            await interaction.response.send_message(
                "📦 Você não tem essa lootbox.",
                ephemeral=True
            )
            return

<<<<<<< Updated upstream
        # recompensa baseada no tipo da box
        rewards = {
            "box_comum": [
                (random.randint(400, 500), "🪙 comum"),
            ],
            "box_raro": [
                (random.randint(500, 700), "✨ raro"),
            ],
            "box_epico": [
                (random.randint(700, 900), "💎 épico"),
            ],
            "box_lendario": [
                (random.randint(1000, 3000), "👑 lendário"),
            ],
            "box_mitico": [
                ("double", "🌟 mítico")
            ]
        }

        if box_id not in rewards:
            await interaction.response.send_message(
                "❌ Essa box não existe.",
                ephemeral=True
            )
            return

        reward, rarity = random.choice(rewards[box_id])

        coins, _, _ = self.get_user(interaction.user.id)

        if reward == "double":
            reward = coins * 2

        # adiciona coins
        self.add_coins(interaction.user.id, reward)

        embed = discord.Embed(
            title="📦 Lootbox aberta!",
            description=f"{rarity}\nVocê ganhou **{reward} coins**",
            color=0xf1c40f
        )

        await interaction.response.send_message(embed=embed)
=======
        rewards = [
            (random.randint(400, 500), "🪙 comum"),
            (random.randint(500, 700), "✨ raro"),
            (random.randint(700, 900), "💎 épico"),
            (random.randint(1000, 3000), "👑 lendário"),
            (coins * 2, "🌟 mítico")
        ]

        reward, rarity = random.choices(
            rewards,
            weights=[60, 25, 10, 5, 1]
        )[0]

        pool = await get_connection()
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE economy SET boxes = boxes - 1, coins = coins + $1 WHERE user_id=$2",
                reward, interaction.user.id
            )

        await interaction.response.send_message(
            f"📦 Lootbox aberta!\n{rarity}\nVocê ganhou **{reward} coins**"
        )
>>>>>>> Stashed changes

    # ================= TRANSFERÊNCIA =================

    @economia.command(name="pay", description="Enviar coins")
    async def pay(self, interaction: discord.Interaction, usuario: discord.Member, quantia: int):

        if usuario.id == interaction.user.id:
            await interaction.response.send_message("❌ Você não pode pagar a si mesmo.", ephemeral=True)
            return

        if quantia <= 0:
            await interaction.response.send_message("❌ Quantia inválida.", ephemeral=True)
            return

        coins, _, _, _ = await self.get_user(interaction.user.id)

        if quantia > coins:
            await interaction.response.send_message("❌ Coins insuficientes.", ephemeral=True)
            return

        taxa = int(quantia * 0.05)
        recebido = quantia - taxa

        pool = await get_connection()
        async with pool.acquire() as conn:

            await conn.execute(
                "UPDATE economy SET coins = coins - $1 WHERE user_id=$2",
                quantia, interaction.user.id
            )

            await conn.execute(
                "INSERT INTO economy (user_id, coins) VALUES ($1,0) ON CONFLICT (user_id) DO NOTHING",
                usuario.id
            )

            await conn.execute(
                "UPDATE economy SET coins = coins + $1 WHERE user_id=$2",
                recebido, usuario.id
            )

        embed = discord.Embed(
            title="💸 Transferência",
            description=(
                f"{interaction.user.mention} enviou **{recebido} coins** para {usuario.mention}\n\n"
                f"💰 Valor: `{quantia}`\n🏦 Taxa: `{taxa}`"
            ),
            color=0x2ecc71
        )

        await interaction.response.send_message(embed=embed)

    # ================= LOJA =================

    @economia.command(name="lojinha", description="Loja diária")
    async def shop(self, interaction: discord.Interaction):

        today = int(datetime.datetime.utcnow().strftime("%Y%m%d"))
        random.seed(today)

        items = [
            ("📦 Lootbox", 500),
            ("🎰 Ticket de cassino", 300),
            ("💎 Gem misteriosa", 1200),
            ("🍀 Amuleto", 800),
            ("🎨 Cor", 2000),
            ("⚡ Boost", 1000)
        ]

        shop_items = random.sample(items, 3)

        text = "\n".join(
            [f"{i+1}. {item[0]} — `{item[1]} coins`" for i, item in enumerate(shop_items)]
        )

        embed = discord.Embed(
            title="🛒 Loja diária",
            description=text,
            color=0x3498db
        )

        await interaction.response.send_message(embed=embed)

    # ================= ERROS =================

    async def cog_app_command_error(self, interaction: discord.Interaction, error):

        if isinstance(error, app_commands.CommandOnCooldown):

            segundos = int(error.retry_after)
            minutos = segundos // 60
            segundos = segundos % 60

            await interaction.response.send_message(
                f"Tente novamente em **{minutos}m {segundos}s**."
            )

<<<<<<< Updated upstream
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT item_id, nome, preco_base, emoji
            FROM items
        """)

        items = cursor.fetchall()
        conn.close()

        if not items:
            await interaction.response.send_message(
                "A loja está vazia.",
                ephemeral=True
            )
            return

        # seed baseada no dia
        today = int(datetime.datetime.utcnow().strftime("%Y%m%d"))
        random.seed(today)

        # pega até 9 itens
        shop_items = random.sample(items, min(9, len(items)))

        text = ""

        for i, item in enumerate(shop_items, start=1):

            item_id, nome, preco, emoji = item

            text += f"{i}. {emoji} **{nome}** — `{preco} coins`\n"

        embed = discord.Embed(
            title="🛒 Loja diária",
            description=text,
            color=0x3498db
        )

        embed.set_footer(text="A loja muda todos os dias!")

        await interaction.response.send_message(embed=embed)
=======
>>>>>>> Stashed changes

    @economia.command(name="inventario", description="Veja seus itens")
    async def inventario(self, interaction: discord.Interaction):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT item_id, quantidade
            FROM members_inventory
            WHERE user_id=%s
        """, (interaction.user.id,))

        items = cursor.fetchall()
        conn.close()

        if not items:
            await interaction.response.send_message("📦 Inventário vazio.")
            return

        text = ""

        for item_id, qtd in items:
            text += f"{item_id} — {qtd}\n"

        embed = discord.Embed(
            title="🎒 Inventário",
            description=text,
            color=0x9b59b6
        )

        await interaction.response.send_message(embed=embed)

    @economia.command(name="mercado", description="Ver itens à venda")
    async def mercado(self, interaction: discord.Interaction):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT listing_id, seller_id, item_id, quantidade, preco
            FROM marketplace
            ORDER BY listing_id
            LIMIT 10
        """)

        listings = cursor.fetchall()
        conn.close()

        if not listings:
            await interaction.response.send_message("🛒 Mercado vazio.")
            return

        text = ""

        for l in listings:

            listing_id, seller_id, item_id, qtd, preco = l

            user = self.bot.get_user(seller_id)

            name = user.name if user else "Desconhecido"

            text += f"ID `{listing_id}` • {item_id} x{qtd} — {preco} coins (vendedor: {name})\n"

        embed = discord.Embed(
            title="🛒 Mercado de jogadores",
            description=text,
            color=0xe67e22
        )

        await interaction.response.send_message(embed=embed)

    @economia.command(name="vender", description="Colocar item à venda")
    async def vender(
        self,
        interaction: discord.Interaction,
        item_id: str,
        quantidade: int,
        preco: int
    ):

        if quantidade <= 0 or preco <= 0:
            await interaction.response.send_message("Valores inválidos.", ephemeral=True)
            return

        ok = self.remove_item(interaction.user.id, item_id, quantidade)

        if not ok:
            await interaction.response.send_message("Você não tem esse item.", ephemeral=True)
            return

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO marketplace (seller_id, item_id, quantidade, preco)
            VALUES (%s,%s,%s,%s)
        """, (interaction.user.id, item_id, quantidade, preco))

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"🛒 Item listado!\n{item_id} x{quantidade} por {preco} coins."
        )

    @economia.command(name="comprar_item", description="Comprar item do mercado")
    async def comprar_item(
        self,
        interaction: discord.Interaction,
        listing_id: int
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT seller_id, item_id, quantidade, preco
            FROM marketplace
            WHERE listing_id=%s
        """, (listing_id,))

        listing = cursor.fetchone()

        if not listing:
            conn.close()
            await interaction.response.send_message("Item não encontrado.", ephemeral=True)
            return

        seller_id, item_id, qtd, preco = listing

        coins, _, _ = self.get_user(interaction.user.id)

        if coins < preco:
            conn.close()
            await interaction.response.send_message("Coins insuficientes.", ephemeral=True)
            return

        # taxa 10%
        taxa = int(preco * 0.10)
        recebido = preco - taxa

        try:

            cursor.execute("BEGIN")

            cursor.execute(
                "UPDATE economy SET coins = coins - %s WHERE user_id=%s",
                (preco, interaction.user.id)
            )

            cursor.execute(
                "UPDATE economy SET coins = coins + %s WHERE user_id=%s",
                (recebido, seller_id)
            )

            cursor.execute(
                "DELETE FROM marketplace WHERE listing_id=%s",
                (listing_id,)
            )

            conn.commit()

        except:
            conn.rollback()
            conn.close()
            await interaction.response.send_message("Erro na compra.")
            return

        conn.close()

        self.add_item(interaction.user.id, item_id, qtd)

        await interaction.response.send_message(
            f"✅ Compra realizada!\nVocê recebeu **{item_id} x{qtd}**"
        )

async def setup(bot):
    await bot.add_cog(Economia(bot))