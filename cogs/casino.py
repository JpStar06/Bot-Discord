import discord
from discord import app_commands
from discord.ext import commands
import random
from database import get_connection


class Casino(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    casino = app_commands.Group(name="casino", description="Jogos de aposta")

    # pegar coins
    def get_coins(self, user_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT coins FROM economy WHERE user_id=%s",
            (user_id,)
        )

        result = cursor.fetchone()

        if not result:
            cursor.execute(
                "INSERT INTO economy (user_id, coins) VALUES (%s,%s)",
                (user_id, 0)
            )
            conn.commit()
            conn.close()
            return 0

        conn.close()
        return result[0]

    # adicionar coins
    def add_coins(self, user_id, amount):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE economy SET coins = coins + %s WHERE user_id=%s",
            (amount, user_id)
        )

        conn.commit()
        conn.close()

    # COINFLIP
    @casino.command(name="coinflip", description="Cara ou coroa")
    @app_commands.checks.cooldown(15, 1200)
    async def coinflip(
        self,
        interaction: discord.Interaction,
        aposta: int,
        escolha: str
    ):

        escolha = escolha.lower()
        if escolha not in ["cara", "coroa"]:
            await interaction.response.send_message(
                "Escolha `cara` ou `coroa`",
                ephemeral=True
            )
            return

        coins = self.get_coins(interaction.user.id)

        if aposta > coins:
            await interaction.response.send_message(
                "Você não tem coins suficientes.",
                ephemeral=True
            )
            return

        resultado = random.choice(["cara", "coroa"])

        if escolha == resultado:
            self.add_coins(interaction.user.id, aposta)
            msg = f"🪙 **{resultado}**\nVocê ganhou `{aposta}` coins!"
        else:
            self.add_coins(interaction.user.id, -aposta)
            msg = f"🪙 **{resultado}**\nVocê perdeu `{aposta}` coins."

        await interaction.response.send_message(msg)
    
    # DICE
    @casino.command(name="dice", description="Jogue dados")
    @app_commands.checks.cooldown(15, 1200)
    async def dice(self, interaction: discord.Interaction, aposta: int):

        coins = self.get_coins(interaction.user.id)

        if aposta > coins:
            await interaction.response.send_message(
                "Coins insuficientes.",
                ephemeral=True
            )
            return

        player = random.randint(1, 6)
        bot = random.randint(1, 6)

        if player > bot:
            self.add_coins(interaction.user.id, aposta)
            resultado = f"🎲 Você: {player}\n🎲 Bot: {bot}\nVocê ganhou `{aposta}` coins!"
        elif player < bot:
            self.add_coins(interaction.user.id, -aposta)
            resultado = f"🎲 Você: {player}\n🎲 Bot: {bot}\nVocê perdeu `{aposta}` coins."
        else:
            resultado = f"🎲 Você: {player}\n🎲 Bot: {bot}\nEmpate!"

        await interaction.response.send_message(resultado)

    # SLOTS
    @casino.command(name="slots", description="Caça-níquel")
    @app_commands.checks.cooldown(15, 1200)
    async def slots(self, interaction: discord.Interaction, aposta: int):

        coins = self.get_coins(interaction.user.id)

        if aposta > coins:
            await interaction.response.send_message(
                "Coins insuficientes.",
                ephemeral=True
            )
            return

        emojis = ["🍒", "🍋", "🍉", "⭐", "💎", "💶", "🪙"]

        r1 = random.choice(emojis)
        r2 = random.choice(emojis)
        r3 = random.choice(emojis)

        resultado = f"{r1} | {r2} | {r3}\n"

        if r1 == r2 == r3:
            ganho = aposta * 6
            self.add_coins(interaction.user.id, ganho)
            resultado += f"🎉 JACKPOT! Você ganhou `{ganho}` coins!"
        elif r1 == r2 or r2 == r3 or r1 == r3:
            ganho = aposta * 3
            self.add_coins(interaction.user.id, ganho)
            resultado += f"✨ Você ganhou `{ganho}` coins!"
        else:
            self.add_coins(interaction.user.id, -aposta)
            resultado += f"💀 Você perdeu `{aposta}` coins."

        await interaction.response.send_message(resultado)

    async def cog_app_command_error(self, interaction: discord.Interaction, error):

        if isinstance(error, app_commands.CommandOnCooldown):

            segundos = int(error.retry_after)
            minutos = segundos // 60
            segundos = segundos % 60

            await interaction.response.send_message(
                f"🎰 Você atingiu o limite de **30 jogadas**.\n"
                f"Tente novamente em **{minutos}m {segundos}s ou jogue outro jogo**."
            )


async def setup(bot):
    await bot.add_cog(Casino(bot))