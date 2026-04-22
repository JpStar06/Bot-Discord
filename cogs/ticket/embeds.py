import discord

class TicketEmbed:

    @staticmethod
    def painel(data: dict):
        embed = discord.Embed(
            title=data.get("titulo", "Sem título"),
            description=data.get("descricao", "Sem descrição"),
            color=data.get("cor", 0x3498db)
        )

        if data.get("imagem"):
            embed.set_image(url=data["imagem"])

        return embed

    @staticmethod
    def topico(data: dict):
        embed = discord.Embed(
            title=data.get("titulo_cliente", "Ticket"),
            description=data.get("descricao_cliente", "Aguarde atendimento"),
            color=data.get("cor_cliente", 0xFF0000)
        )

        if data.get("imagem_cliente"):
            embed.set_image(url=data["imagem_cliente"])

        return embed