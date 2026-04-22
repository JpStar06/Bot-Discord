from database import get_connection
import discord


class TicketService:

    # ---------- CREATE ----------
    @staticmethod
    async def create_ticket(guild_id: int, channel_id: int):
        pool = get_connection()

        async with pool.acquire() as conn:
            ticket_id = await conn.fetchval(
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

        return ticket_id

    # ---------- GET ----------
    @staticmethod
    async def get_ticket(guild_id: int, ticket_id: int):
        pool = get_connection()

        async with pool.acquire() as conn:
            data = await conn.fetchrow(
                "SELECT * FROM tickets WHERE id=$1 AND guild_id=$2",
                ticket_id,
                guild_id,
            )

        return data

    # ---------- UPDATE PANEL ----------
    @staticmethod
    async def update_panel(guild_id: int, ticket_id: int, data: dict):
        pool = get_connection()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE tickets
                SET titulo=$1, descricao=$2, cor=$3, imagem=$4
                WHERE id=$5 AND guild_id=$6
                """,
                data["titulo"],
                data["descricao"],
                data["cor"],
                data.get("imagem"),
                ticket_id,
                guild_id,
            )

    # ---------- UPDATE TOPIC ----------
    @staticmethod
    async def update_topic(guild_id: int, ticket_id: int, data: dict):
        pool = get_connection()

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
    @staticmethod
    async def create_thread(
        interaction: discord.Interaction,
        ticket_id: int,
        user: discord.Member,
    ):
        pool = get_connection()

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