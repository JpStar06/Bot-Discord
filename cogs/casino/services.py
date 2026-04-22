from database import get_connection
import random

def spin_slots(aposta: int):
    EMOJIS = ["🍒", "🍋", "🍉", "⭐", "💎", "💶", "🪙"]
    r1 = random.choice(EMOJIS)
    r2 = random.choice(EMOJIS)
    r3 = random.choice(EMOJIS)

    if r1 == r2 == r3:
        return (r1, r2, r3), aposta * 6, "jackpot"
    elif r1 == r2 or r2 == r3 or r1 == r3:
        return (r1, r2, r3), aposta * 3, "win"
    else:
        return (r1, r2, r3), -aposta, "lose"
    

def draw_card():
    suits = ["♣️", "♠️", "♥️", "♦️"]
    values = [
        ("A", 11),
        ("2", 2), ("3", 3), ("4", 4), ("5", 5),
        ("6", 6), ("7", 7), ("8", 8), ("9", 9),
        ("10", 10), ("J", 10), ("Q", 10), ("K", 10)
    ]

    value, points = random.choice(values)
    suit = random.choice(suits)

    return {"display": f"{value}{suit}", "value": points}

def calculate_hand(hand):
    total = sum(card["value"] for card in hand)

    # tratar Ás
    aces = sum(1 for card in hand if card["value"] == 11)

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total

def start_game():
    player = [draw_card(), draw_card()]
    dealer = [draw_card(), draw_card()]

    return player, dealer