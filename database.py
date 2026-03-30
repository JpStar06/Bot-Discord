import asyncpg
import os

pool = None

# iniciar conexão com pool
async def init_db():
    global pool

    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não encontrada no .env")

    pool = await asyncpg.create_pool(
        DATABASE_URL,
        ssl="require",
        min_size=1,
        max_size=5
    )

    print("✅ Banco conectado com sucesso!")

    # cria tabelas
    async with pool.acquire() as conn:

        # embeds
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS embeds (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            title TEXT,
            description TEXT,
            color INTEGER,
            image TEXT
        )
        """)

        # tickets
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            titulo TEXT,
            descricao TEXT,
            cor INTEGER,
            emoji TEXT,
            canal_id BIGINT,
            staff_id BIGINT,
            imagem TEXT
        )
        """)

        # economy
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS economy (
            user_id BIGINT PRIMARY KEY,
            coins BIGINT NOT NULL DEFAULT 0,
            last_daily BIGINT NOT NULL DEFAULT 0,
            daily_streak BIGINT NOT NULL DEFAULT 0,
            boxes BIGINT NOT NULL DEFAULT 0
        )
        """)

        # reminders
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            channel_id BIGINT,
            embed_id INTEGER,
            horario TEXT
        )
        """)

        print("📦 Tabelas verificadas/criadas com sucesso!")

    cursor.execute("""
    CREATE TABLE items (
        item_id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        descricao TEXT,
        tipo TEXT,
        raridade TEXT,
        preco_base INTEGER,
        emoji TEXT,
        usavel BOLEAN
    )
""")
    
    cursor.execute("""
    CREATE TABLE members_inventory (
        user_id BIGINT,
        item_id TEXT,
        quantidade INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, item_id
    )
""")
    
    cursor.execute("""
    CREATE TABLE marketplace (
        listing_id SERIAL PRIMARY KEY,
        seller_id BIGINT,
        item_id TEXT,
        quantidade INT,
        preco INT
    )
""")

# pegar conexão do pool
async def get_connection():
    if not pool:
        raise ValueError("Pool não inicializado. Use init_db() primeiro.")
    return pool