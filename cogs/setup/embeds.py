import discord
def embed1():
    embed = discord.Embed(
        title="📌 Bem-vindo ao tutorial da Aiko!",
        description=(
            "Aqui vou te mostrar como usar o sistema de tickets, embeds e economia da Aiko!\n\nPrometo que tudo será bem simples e fácil de entender, então vamos lá! :3"
        ),
        color=discord.Color.pink()
    )
    return embed

def embed2():
    embed = discord.Embed(
        title="🎫 Sistema de Tickets",
        description=(
            "O sistema de tickets da Aiko é bem simples e eficiente. Ele permite que os membros criem tickets para solicitar ajuda ou suporte, e a equipe de staff pode gerenciar esses tickets facilmente. E tem o toque final, quando os tickets são fechados eles enviam um transcript para a staff e o usuário, então tudo é salvo.\n\n"
            "Para criar o seu primeiro ticket, use `/ickets criar`, isso ira criar um ticket padrão, depois use `/ickets editar <id>` para personalizar o ticket, nas opções você poderá alterar o título, descrição, cor, atendente(o cargo que ira atender o ticket) e até uma imagem.\n\n E por fim use `/ickets enviar <id> <canal>` para enviar o ticket para um canal específico."
            "\n\nEu utilizo sistemas de botões tanto para abrir e fechar tickets, quanto para para edita-los, então é tudo bem intuitivo!"
        ),
        color=discord.Color.green()
    )
    return embed