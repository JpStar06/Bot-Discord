import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)


def setup_database():

    conn = get_connection()
    cursor = conn.cursor()

    # tabela embeds
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS embeds (
        id SERIAL PRIMARY KEY,
        guild_id BIGINT,
        title TEXT,
        description TEXT,
        color INTEGER,
        image TEXT
    )
    """)

    # tabela tickets
    cursor.execute("""
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
    print("DATABASE_URL:", DATABASE_URL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS economy (
        user_id BIGINT PRIMARY KEY,
        coins BIGINT NOT NULL DEFAULT 0,
        last_daily BIGINT NOT NULL DEFAULT 0,
        daily_streak BIGINT NOT NULL DEFAULT 0,
        boxes BIGINT NOT NULL DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id SERIAL PRIMARY KEY,
        guild_id BIGINT,
        channel_id BIGINT,
        embed_id INTEGER,
        horario TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE items (
        item_id TEXT PRIMARY KEY,
        nome TEXT NOT NULL,
        descricao TEXT,
        tipo TEXT,
        raridade TEXT,
        preco_base INTEGER,
        emoji TEXT
    )
""")
    
    cursor.execute("""
    CREATE TABLE members_inventory (
        user_id BIGINT,
        item_id TEXT,
        quantidade INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, item_id)
    )
""")

    conn.commit()
    conn.close()
