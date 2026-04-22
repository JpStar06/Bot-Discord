import discord

class TicketEmbed:

    @staticmethod
    def painel(data):
        embed = discord.Embed(
            title=data["titulo"],
            description=data["descricao"],
            color=data["cor"]
        )

        if data.get("imagem"):
            embed.set_image(url=data["imagem"])

        return embed

    @staticmethod
    def topico(data):
        embed = discord.Embed(
            title=data["titulo_cliente"] or "Ticket",
            description=data["descricao_cliente"] or "Aguarde atendimento",
            color=data["cor_cliente"] or 0xFF0000
        )

        if data.get("imagem_cliente"):
            embed.set_image(url=data["imagem_cliente"])

        return embed
    
def acerto(msg: str):
    return discord.Embed(
        title="concluido",
        description=msg,
        color=discord.Color.green()
    )