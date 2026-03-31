import discord
from discord.ext import commands
from discord import app_commands
import random
from .casino import Casino


# 🎴 cartas com símbolo
cards = [
    "A♠️","2♠️","3♠️","4♠️","5♠️","6♠️","7♠️","8♠️","9♠️","10♠️","J♠️","Q♠️","K♠️",
    "A♥️","2♥️","3♥️","4♥️","5♥️","6♥️","7♥️","8♥️","9♥️","10♥️","J♥️","Q♥️","K♥️",
]

def card_value(card):
    if card.startswith(("J","Q","K")):
        return 10
    if card.startswith("A"):
        return 11
    return int(card[:-2])

def hand_value(hand):
    total = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c.startswith("A"))

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total

def draw_card():
    return random.choice(cards)


# 🎮 View (botões)
class BlackjackView(discord.ui.View):
    def __init__(self, cog, interaction, player_hand, dealer_hand, bet):
        super().__init__(timeout=60)
        self.cog = cog
        self.interaction_user = interaction.user
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.bet = bet

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.interaction_user  # 🔒 só quem iniciou joga

    def build_embed(self, hide_dealer=True):
        dealer_cards = f"{self.dealer_hand[0]}, ?" if hide_dealer else ", ".join(self.dealer_hand)

        return discord.Embed(
            title="🃏 Blackjack",
            description=(
                f"**Sua mão:** {', '.join(self.player_hand)} ({hand_value(self.player_hand)})\n"
                f"**Dealer:** {dealer_cards}"
            ),
            color=discord.Color.green()
        )

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player_hand.append(draw_card())

        if hand_value(self.player_hand) > 21:
            embed = discord.Embed(
                title="💥 Bust!",
                description=f"Você perdeu!\nMão: {', '.join(self.player_hand)}",
                color=discord.Color.red()
            )
            return await interaction.response.edit_message(embed=embed, view=None)

        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        while hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(draw_card())

        player = hand_value(self.player_hand)
        dealer = hand_value(self.dealer_hand)

        if dealer > 21 or player > dealer:
            result = "🎉 Você ganhou!"
            color = discord.Color.green()
            await self.cog.add_coins(interaction.user.id, self.bet * 2)

        elif player == dealer:
            result = "🤝 Empate!"
            color = discord.Color.yellow()
            await self.cog.add_coins(interaction.user.id, self.bet)

        else:
            result = "💀 Você perdeu!"
            color = discord.Color.red()

        embed = discord.Embed(
            title="🃏 Resultado",
            description=(
                f"{result}\n\n"
                f"**Sua mão:** {', '.join(self.player_hand)} ({player})\n"
                f"**Dealer:** {', '.join(self.dealer_hand)} ({dealer})"
            ),
            color=color
        )

        await interaction.response.edit_message(embed=embed, view=None)


# 🎯 comando
class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    casino = Casino.casino

    async def add_coins(self, user_id, amount):
        # 👉 conecta com seu sistema real depois
        pass

    async def get_user(self, user_id):
        return {"coins": 1000}  # mock

    @casino.command(name="blackjack", description="Jogar blackjack")
    @app_commands.describe(bet="Quantidade de coins apostada")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        user = await self.get_user(interaction.user.id)

        if bet <= 0 or user["coins"] < bet:
            return await interaction.response.send_message(
                "❌ Aposta inválida.", ephemeral=True
            )

        await self.add_coins(interaction.user.id, -bet)

        player_hand = [draw_card(), draw_card()]
        dealer_hand = [draw_card(), draw_card()]

        view = BlackjackView(self, interaction, player_hand, dealer_hand, bet)

        await interaction.response.send_message(
            embed=view.build_embed(),
            view=view
        )


async def setup(bot):
    await bot.add_cog(Blackjack(bot))