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
        last_daily BIGINT NOT NULL DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
