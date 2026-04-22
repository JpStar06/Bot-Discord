import asyncpg
import os
import discord
from database import get_connection



# ---------- CREATE ----------

async def criarticket(guild_id: int, channel_id: int):
    pool = get_connection
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO tickets (
                guild_id, titulo, descricao, cor, emoji, canal_id,
                titulo_cliente, descricao_cliente, cor_cliente
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
            RETURNING id
            """,
            guild_id,
            "Suporte",
            "Clique no botão abaixo para abrir um ticket.",
            0x3498DB,
            "🎫",
            channel_id,
            "ESPERE SER ATENDIDO",
            "Nossa equipe pode estar ocupada.",
            0xFF0000,
        )
    return row["id"]

#---------LISTAR TICKET--------
async def listarticket(guild_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        tickets = await conn.fetch("SELECT id, title FROM tickets WHERE guild_id=$1", guild_id)

    return tickets

# ---------- GET ----------

async def buscar_ticket(guild_id: int, ticket_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT title, description, color, image FROM tickets WHERE id=$1 AND guild_id=$2", ticket_id, guild_id)

        if not row:
            return None

        return dict(row)

# ---------- UPDATE ----------

async def editar_ticket(guild_id: int, embed_id: int, novo_titulo=None, nova_descricao=None, nova_cor=None, imagem_url=None):
    pool = get_connection()

    async with pool.acquire() as conn:
        ticket_data = await conn.fetchrow(
            "SELECT title, description, color, image FROM tickets WHERE id=$1 AND guild_id=$2",
            embed_id, guild_id
        )

        if not ticket_data:
            return None

        title = novo_titulo or ticket_data["title"]
        description = nova_descricao or ticket_data["description"]
        color = nova_cor or ticket_data["color"]
        image = imagem_url or ticket_data["image"]

        await conn.execute("""
            UPDATE tickets
            SET title=$1, description=$2, color=$3, image=$4
            WHERE id=$5 AND guild_id=$6
        """, title, description, color, image, embed_id, guild_id)

        return {
            "title": title,
            "description": description,
            "color": color,
            "image": image
        }

async def update_topic(guild_id: int, ticket_id: int, data: dict):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE tickets
            SET
                titulo_cliente=$1,
                descricao_cliente=$2,
                cor_cliente=$3,
                imagem_cliente=$4,
                staff_id=$5
            WHERE id=$6 AND guild_id=$7
            """,
            data["titulo_cliente"],
            data["descricao_cliente"],
            data["cor_cliente"],
            data.get("imagem_cliente"),
            data.get("staff_id"),
            ticket_id,
            guild_id,
        )

# ---------- THREAD ----------

async def create_thread(
    interaction: discord.Interaction,
    ticket_id: int,
    user: discord.Member,
):
    pool = await get_pool()
    async with pool.acquire() as conn:
        data = await conn.fetchrow(
            """
            SELECT
                titulo_cliente, descricao_cliente,
                cor_cliente, imagem_cliente, staff_id
            FROM tickets
            WHERE id=$1 AND guild_id=$2
            """,
            ticket_id,
            interaction.guild.id,
        )

    if not data:
        return None, "Configuração não encontrada."

    try:
        thread = await interaction.channel.create_thread(
            name=f"ticket-{user.name}",
            type=discord.ChannelType.private_thread,
        )
        await thread.add_user(user)

        if data["staff_id"]:
            role = interaction.guild.get_role(data["staff_id"])
            if role:
                for member in role.members:
                    await thread.add_user(member)

    except discord.HTTPException as e:
        return None, str(e)

    return thread, data
