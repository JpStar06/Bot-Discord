from database import get_connection
import datetime
import random

# -------------------- USER --------------------
async def get_user(user_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT coins, daily_streak, last_daily, boxes FROM economy WHERE user_id=$1",
            user_id
        )

        if not user:
            await conn.execute(
                "INSERT INTO economy (user_id, coins, daily_streak, boxes) VALUES ($1, 0, 0, 0)",
                user_id
            )
            return {
                "coins": 0,
                "daily_streak": 0,
                "last_daily": None,
                "boxes": 0
            }

        return dict(user)
        
# -------------------- COINS --------------------
async def add_coins(user_id: int, amount: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE economy SET coins = coins + $1 WHERE user_id=$2",
            amount, user_id
        )

async def get_coins(user_id: int) -> int:
    pool = get_connection()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT coins FROM economy WHERE user_id=$1", user_id
        )

        if not row:
            await conn.execute(
                "INSERT INTO economy (user_id, coins) VALUES ($1, $2)",
                user_id, 0
            )
            return 0

        return row["coins"]
# -------------------- DAILY --------------------
async def daily(user_id: int):
    pool = get_connection()
    user = await get_user(user_id)

    now = int(datetime.datetime.utcnow().strftime("%Y%m%d"))

    if user["last_daily"] == now:
        return {"already_claimed": True}

    streak = user["daily_streak"] or 0
    streak += 1
    reward = random.randint(100, 500) + (streak * 20)

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE economy SET coins=coins+$1, daily_streak=$2, last_daily=$3 WHERE user_id=$4",
            reward, streak, now, user_id
        )

    return {
        "reward": reward,
        "streak": streak,
        "already_claimed": False
    }

# -------------------- WORK --------------------
async def work(user_id: int):
    jobs = ["programador", "minerador", "chef", "hacker", "músico"]
    job = random.choice(jobs)
    reward = random.randint(100, 400)

    await add_coins(user_id, reward)

    return {
        "job": job,
        "reward": reward
    }

# -------------------- LOOTBOX --------------------

async def open_box(user_id: int):
    pool = get_connection()
    user = await get_user(user_id)

    if user["boxes"] <= 0:
        return None

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE economy SET boxes = boxes - 1 WHERE user_id=$1",
            user_id
        )

    rewards = [
        (random.randint(400, 500), "🪙 comum"),
        (random.randint(500, 700), "✨ raro"),
        (random.randint(700, 900), "💎 épico"),
        (random.randint(1000, 3000), "👑 lendário"),
        (user["coins"] * 2, "🌟 mítico")
    ]

    reward, rarity = random.choices(rewards, weights=[60, 25, 10, 5, 1])[0]

    await add_coins(user_id, reward)

    return {
        "reward": reward,
        "rarity": rarity
    }

async def buy_box(user_id: int):
    pool = get_connection()
    user = await get_user(user_id)

    price = 500

    if user["coins"] < price:
        return {
            "success": False,
            "faltante": price - user["coins"]
        }

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE economy SET coins = coins - $1, boxes = boxes + 1 WHERE user_id=$2",
            price, user_id
        )

    return {
        "success": True
    }

# -------------------- PAY --------------------
async def transfer(sender_id: int, target_id: int, amount: int):
    pool = get_connection()

    sender = await get_user(sender_id)

    if amount <= 99:
        return {"error": "invalid_amount"}

    if amount > sender["coins"]:
        return {"error": "no_money"}

    taxa = int(amount * 0.02)
    recebido = amount - taxa

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE economy SET coins = coins - $1 WHERE user_id=$2",
            amount, sender_id
        )

        await conn.execute(
            "INSERT INTO economy (user_id, coins) VALUES ($1, 0) ON CONFLICT (user_id) DO NOTHING",
            target_id
        )

        await conn.execute(
            "UPDATE economy SET coins = coins + $1 WHERE user_id=$2",
            recebido, target_id
        )

    return {
        "enviado": amount,
        "recebido": recebido,
        "taxa": taxa,
        "target_id": target_id
    }

async def get_ranking(limit: int = 10):
    pool = get_connection()

    async with pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT user_id, coins FROM economy ORDER BY coins DESC LIMIT $1",
            limit
        )

    return [dict(u) for u in users]