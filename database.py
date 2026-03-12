import os
import psycopg2
from psycopg2 import pool

connection_pool = None


def init_db():
    global connection_pool

    connection_pool = psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host=os.getenv("PGHOST"),
        database=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        port=os.getenv("PGPORT")
    )

    print("✅ Pool de conexões com o PostgreSQL criado.")


def get_connection():
    if connection_pool is None:
        raise Exception("Pool de conexões não inicializado.")
    return connection_pool.getconn()


def release_connection(conn):
    if connection_pool:
        connection_pool.putconn(conn)


def close_all_connections():
    if connection_pool:
        connection_pool.closeall()


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
    cursor.close()
    release_connection(conn)

    print("✅ Tabelas verificadas/criadas.")