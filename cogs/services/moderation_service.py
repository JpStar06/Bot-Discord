import discord

async def ban_member(guild, member, reason):
    await guild.ban(member, reason=reason)

async def kick_member(member, reason):
    await member.kick(reason=reason)

async def mute_member(member, minutes, reason):
    until = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await member.timeout(until, reason=reason)