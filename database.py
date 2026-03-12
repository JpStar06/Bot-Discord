import psycopg2
import os

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("PGHOST"),
        database=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        port=os.getenv("PGPORT")
    )
    return conn

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()