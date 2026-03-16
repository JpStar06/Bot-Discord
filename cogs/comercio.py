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
        try:

            await interaction.response.defer()

            data = self.get_user(interaction.user.id)

            if not data:
                coins, streak, last = 0, 0, None
            else:
                coins, streak, last = data

            now = int(datetime.datetime.utcnow().strftime("%Y%m%d"))

            # verifica ultimo daily
            if last == now:
                await interaction.followup.send(
                    "⏳ Você já pegou o daily hoje.",
                    ephemeral=True
                )
                return

            # aumenta streak
            streak = streak or 0
            streak += 1
            reward = random.randint(100, 500) + (streak * 20)

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE economy SET coins = coins + %s, daily_streak = %s, last_daily = %s WHERE user_id = %s",
                (reward, streak, now, interaction.user.id)
            )

            conn.commit()
            conn.close()

            await interaction.followup.send(
                f"🎁 Daily coletado!\n+{reward} coins\n🔥 Streak: {streak}"
            )
        except Exception as e:
            print(e)
        
    # work
    @economia.command(name="work", description="Trabalhe para ganhar coins")
    @app_commands.checks.cooldown(8, 600)
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
            f"💼 Você trabalhou como **{job}** por 1 hora\ne recebeu {reward} coins"
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

        if not users:
            await interaction.response.send_message("Nenhum dado no ranking.")
            return

        text = ""

        for i, u in enumerate(users, start=1):

            user = self.bot.get_user(int(u[0]))

            if not user:
                try:
                    user = await self.bot.fetch_user(int(u[0]))
                except:
                    continue

            text += f"{i}. {user.name} — {u[1]} coins\n"

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
            "SELECT boxes, coins FROM economy WHERE user_id=%s",
            (interaction.user.id,)
        )

        result = cursor.fetchone()

        if not result or result[0] <= 0:
            await interaction.response.send_message(
                "📦 Você não tem lootboxes.",
                ephemeral=True
            )
            return

        boxes, coins = result

        cursor.execute(
            "UPDATE economy SET boxes = boxes - 1 WHERE user_id=%s",
            (interaction.user.id,)
        )

        conn.commit()

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

        cursor.execute(
            "UPDATE economy SET coins = coins + %s WHERE user_id=%s",
            (reward, interaction.user.id)
        )

        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"📦 Lootbox aberta!\n{rarity}\nVocê ganhou **{reward} coins**"
        )

    @economia.command(name="pay", description="Envie coins para outro usuário")
    async def pay(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        quantia: int
    ):
        try:
            if usuario.id == interaction.user.id:
                await interaction.response.send_message(
                    "❌ Você não pode pagar a si mesmo.",
                    ephemeral=True
                )
                return

            if quantia <= 0:
                await interaction.response.send_message(
                    "❌ Quantia inválida.",
                    ephemeral=True
                )
                return

            coins, _, _ = self.get_user(interaction.user.id)

            if quantia > coins:
                await interaction.response.send_message(
                    "❌ Você não tem coins suficientes.",
                    ephemeral=True
                )
                return

            # taxa de 5%
            taxa = int(quantia * 0.05)
            recebido = quantia - taxa

            conn = get_connection()
            cursor = conn.cursor()

            # remove coins do pagador
            cursor.execute(
                "UPDATE economy SET coins = coins - %s WHERE user_id=%s",
                (quantia, interaction.user.id)
            )

            # garante que o usuário existe
            cursor.execute(
                "INSERT INTO economy (user_id, coins) VALUES (%s,0) ON CONFLICT (user_id) DO NOTHING",
                (usuario.id,)
            )

            # adiciona coins ao destinatário
            cursor.execute(
                "UPDATE economy SET coins = coins + %s WHERE user_id=%s",
                (recebido, usuario.id)
            )

            conn.commit()
            conn.close()

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
        except Exception as e:
            print(e)

    async def cog_app_command_error(self, interaction: discord.Interaction, error):

        if isinstance(error, app_commands.CommandOnCooldown):

            segundos = int(error.retry_after)
            minutos = segundos // 60
            segundos = segundos % 60

            await interaction.response.send_message(
                f"Você ja trabalhou por 8 horas.\n"
                f"De acordo com as leis trabalhistas você só pode trabalhar por 8 horas\n"
                f"Tente novamente em **{minutos}m {segundos}s**."
            )
    
    @economia.command(name="lojinha", description="Veja a loja diária")
    async def shop(self, interaction: discord.Interaction):

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