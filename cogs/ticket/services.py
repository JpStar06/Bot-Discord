import asyncpg
import os
from dotenv import load_dotenv
import discord

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

class TicketService:

    @staticmethod
    async def get_connection():
        return await asyncpg.connect(DATABASE_URL)

    @staticmethod
    async def update_panel(guild_id, ticket_id, data):
        conn = await TicketService.get_connection()

        await conn.execute(
            """
            UPDATE tickets SET 
            titulo=$1, descricao=$2, cor=$3, imagem=$4, staff_id=$5
            WHERE id=$6 AND guild_id=$7
            """,
            data["titulo"],
            data["descricao"],
            data["cor"],
            data["imagem"],
            data.get("staff_id"),
            ticket_id,
            guild_id
        )

        await conn.close()

    @staticmethod
    async def create_thread(interaction, ticket_id, user):
        conn = await TicketService.get_connection()

        data = await conn.fetchrow(
            """
            SELECT titulo_cliente, descricao_cliente, cor_cliente, imagem_cliente, staff_id
            FROM tickets WHERE id=$1 AND guild_id=$2
            """,
            ticket_id,
            interaction.guild.id
        )

        await conn.close()

        if not data:
            return None, "Configuração não encontrada."

        thread = await interaction.channel.create_thread(
            name=f"ticket-{user.name}",
            type=discord.ChannelType.private_thread
        )

        await thread.add_user(user)

        if data["staff_id"]:
            role = interaction.guild.get_role(data["staff_id"])
            if role:
                for member in role.members:
                    try:
                        await thread.add_user(member)
                    except:
                        pass

        return thread, dict(data)