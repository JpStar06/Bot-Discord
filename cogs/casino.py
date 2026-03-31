# cogs/casino.py
import discord
import random
from discord import app_commands
from discord.ext import commands
from database import get_connection


class Casinocomando(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    casino = app_commands.Group(name="casino", description="Jogos de aposta")

    # -------------------- FUNÇÕES DE COINS --------------------
    async def get_coins(self, user_id: int) -> int:
        pool = await get_connection()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT coins FROM economy WHERE user_id=$1", user_id)
            if not row:
                await conn.execute("INSERT INTO economy (user_id, coins) VALUES ($1, $2)", user_id, 0)
                return 0
            return row["coins"]

    async def add_coins(self, user_id: int, amount: int):
        pool = await get_connection()
        async with pool.acquire() as conn:
            await conn.execute("UPDATE economy SET coins = coins + $1 WHERE user_id=$2", amount, user_id)

    # -------------------- COINFLIP --------------------
    @casino.command(name="coinflip", description="Cara ou coroa")
    @app_commands.checks.cooldown(30, 1200)
    async def coinflip(self, interaction: discord.Interaction, aposta: int, escolha: str):
        escolha = escolha.lower()
        if escolha not in ["cara", "coroa"]:
            await interaction.response.send_message("Escolha `cara` ou `coroa`", ephemeral=True)
            return

        coins = await self.get_coins(interaction.user.id)
        if aposta > coins:
            await interaction.response.send_message("Você não tem coins suficientes.", ephemeral=True)
            return

        resultado = random.choice(["cara", "coroa"])
        if escolha == resultado:
            await self.add_coins(interaction.user.id, aposta)
            msg = f"🪙 **{resultado}**\nVocê ganhou `{aposta}` coins!"
        else:
            await self.add_coins(interaction.user.id, -aposta)
            msg = f"🪙 **{resultado}**\nVocê perdeu `{aposta}` coins."

        await interaction.response.send_message(msg)

    # -------------------- DICE --------------------
    @casino.command(name="dice", description="Jogue dados")
    @app_commands.checks.cooldown(30, 1200)
    async def dice(self, interaction: discord.Interaction, aposta: int):
        coins = await self.get_coins(interaction.user.id)
        if aposta > coins:
            await interaction.response.send_message("Coins insuficientes.", ephemeral=True)
            return

        player = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if player > bot_roll:
            await self.add_coins(interaction.user.id, aposta)
            resultado = f"🎲 Você: {player}\n🎲 Bot: {bot_roll}\nVocê ganhou `{aposta}` coins!"
        elif player < bot_roll:
            await self.add_coins(interaction.user.id, -aposta)
            resultado = f"🎲 Você: {player}\n🎲 Bot: {bot_roll}\nVocê perdeu `{aposta}` coins."
        else:
            resultado = f"🎲 Você: {player}\n🎲 Bot: {bot_roll}\nEmpate!"

        await interaction.response.send_message(resultado)

    # -------------------- SLOTS --------------------
    @casino.command(name="slots", description="Caça-níquel")
    @app_commands.checks.cooldown(30, 1200)
    async def slots(self, interaction: discord.Interaction, aposta: int):
        coins = await self.get_coins(interaction.user.id)
        if aposta > coins:
            await interaction.response.send_message("Coins insuficientes.", ephemeral=True)
            return

        emojis = ["🍒", "🍋", "🍉", "⭐", "💎", "💶", "🪙"]
        r1, r2, r3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
        resultado = f"{r1} | {r2} | {r3}\n"

        if r1 == r2 == r3:
            ganho = aposta * 6
            await self.add_coins(interaction.user.id, ganho)
            resultado += f"🎉 JACKPOT! Você ganhou `{ganho}` coins!"
        elif r1 == r2 or r2 == r3 or r1 == r3:
            ganho = aposta * 3
            await self.add_coins(interaction.user.id, ganho)
            resultado += f"✨ Você ganhou `{ganho}` coins!"
        else:
            await self.add_coins(interaction.user.id, -aposta)
            resultado += f"💀 Você perdeu `{aposta}` coins."

        await interaction.response.send_message(resultado)

    # -------------------- ERRO --------------------
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            segundos = int(error.retry_after)
            minutos = segundos // 60
            segundos = segundos % 60
            await interaction.response.send_message(
                f"🎰 Você atingiu o limite de **30 jogadas**.\n"
                f"Tente novamente em **{minutos}m {segundos}s** ou jogue outro jogo.",
                ephemeral=True
            )


# -------------------- SETUP --------------------
async def setup(bot):
    await bot.add_cog(Casinocomando(bot))