import discord

def carteira(msg: str):
    return discord.Embed(
        title="CARTEIRA",
        description=msg,
        color=discord.Color.yellow()
    )

def daily(msg: str):
    return discord.Embed(
        title="COINS DIÁRIA",
        description=msg,
        color=discord.Color.green()
    )

def erro(msg: str):
    return discord.Embed(
        title="Opss!",
        description=msg,
        color=discord.Color.red()
    )

def work(msg: str):
    return discord.Embed(
        title="WORK",
        description=msg,
        color=discord.Color.yellow()
    )

def compra(msg: str):
    return discord.Embed(
        title="COMPRA",
        description=msg,
        color=discord.Color.green()
    )

def ganhou(msg: str):
    return discord.Embed(
        title="GANHOU",
        description=msg,
        color=discord.Color.green()
    )

def pay(msg: str):
    return discord.Embed(
        title="TRANSFERÊNCIA",
        description=msg,
        color=discord.Color.yellow()
    )