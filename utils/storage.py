import json
import os
from utils.event.exp_sustem.helpers import check_level_up

DATA_FILE = os.path.join("data", "users.json")
DATA_EXP_FILE = os.path.join("data", "exp.json")
DATA_MONEY_FILE = os.path.join("data", "money.json")

def ensure_data_dir():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    if not os.path.exists(DATA_EXP_FILE):
        with open(DATA_EXP_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    if not os.path.exists(DATA_MONEY_FILE):
        with open(DATA_MONEY_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

#------------------- USERS --------------------
def get_user_data(discord_id: int) -> dict | None:
    ensure_data_dir()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(str(discord_id))

def get_user_steam_id(discord_id: int) -> int | None:
    user_info = get_user_data(discord_id)
    if not user_info:
        return None
    if isinstance(user_info, dict):
        return user_info.get("account_id")
    return user_info

def save_user_steam_id(discord_id: int, discord_name: str, account_id: int, steam_name: str = "Unknown"):
    ensure_data_dir()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data[str(discord_id)] = {
        "discord_id": discord_id,
        "discord_username": discord_name,
        "account_id": account_id,
        "steam_name": steam_name
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_all_users_data() -> dict:
    """Повертає словник з даними всіх користувачів (Dota-акаунти)."""
    ensure_data_dir()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
#---------------------- USERS END ------------------------------

#---------------------- EXP ------------------------------------
def add_user_exp(user_id: int, xp_amount: int, username: str = None) -> dict:
    ensure_data_dir()
    
    with open(DATA_EXP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    user_key = str(user_id)

    if user_key not in data:
        data[user_key] = {
            "user_id": user_id,
            "username": username or "Unknown",
            "xp": 0,
            "lvl": 1
        }
    else:
        if username:
            data[user_key]["username"] = username

    data[user_key]["xp"] += xp_amount

    with open(DATA_EXP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return data[user_key]

def update_user_exp_and_lvl(user_id: int, new_xp: int, new_lvl: int, username: str = None):
    ensure_data_dir()
    with open(DATA_EXP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    user_key = str(user_id)
    if user_key not in data:
        data[user_key] = {
            "user_id": user_id,
            "username": username or "Unknown",
            "xp": 0,
            "lvl": 1
        }

    data[user_key]["xp"] = new_xp
    data[user_key]["lvl"] = new_lvl
    if username:
        data[user_key]["username"] = username

    with open(DATA_EXP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user_exp(user_id: int) -> dict:
    ensure_data_dir()
    with open(DATA_EXP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    user_key = str(user_id)
    return data.get(user_key, {"user_id": user_id, "xp": 0, "lvl": 1})

def set_user_level(user_id: int, new_lvl: int):
    ensure_data_dir()
    with open(DATA_EXP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    user_key = str(user_id)
    if user_key in data:
        data[user_key]["lvl"] = new_lvl
        with open(DATA_EXP_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def get_top_users(limit: int = 10) -> list[dict]:
    ensure_data_dir()
    with open(DATA_EXP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    users = list(data.values())

    users.sort(key=lambda u: (u.get("lvl", 1), u.get("xp", 0)), reverse=True)

    return users[:limit]

def recalculate_all_levels() -> int:
    ensure_data_dir()
    with open(DATA_EXP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_count = 0
    for user_id, user_info in data.items():
        raw_xp = user_info.get("xp", 0)
        raw_lvl = user_info.get("lvl", 1)

        # Вычисляем правильные целочисленные значения
        clean_xp, clean_lvl, _ = check_level_up(int(raw_xp), int(raw_lvl))
        
        user_info["xp"] = clean_xp
        user_info["lvl"] = clean_lvl
        updated_count += 1

    with open(DATA_EXP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return updated_count

def get_all_exp_data() -> dict:
    ensure_data_dir()
    with open(DATA_EXP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
#-------------------------- EXP END ---------------------------

#-------------------------- MONEY -----------------------------
def change_user_money(user_id: int, money_amount: int, username: str = None) -> dict:
    """Универсальная функция для изменения баланса пользователя (принимает и + и -)"""
    ensure_data_dir()
    
    with open(DATA_MONEY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    user_key = str(user_id)

    if user_key not in data:
        data[user_key] = {
            "user_id": user_id,
            "username": username or "Unknown",
            "money": 0
        }
    elif username:
        data[user_key]["username"] = username

    data[user_key]["money"] += money_amount

    if data[user_key]["money"] < 0:
        data[user_key]["money"] = 0

    with open(DATA_MONEY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return data[user_key]

def add_user_money(user_id: int, money_amount: int, username: str = None) -> dict:
    return change_user_money(user_id, int(money_amount), username)


def remove_user_money(user_id: int, money_amount: int, username: str = None) -> dict:
    return change_user_money(user_id, -int(money_amount), username)


# Backward-compatible aliases for older commands/imports.
def add_user_monay(user_id: int, money_amount: int, username: str = None) -> dict:
    return add_user_money(user_id, money_amount, username)


def remove_usr_monay(user_id: int, money_amount: int, username: str = None) -> dict:
    return remove_user_money(user_id, money_amount, username)

def get_user_money(user_id: int) -> dict:
    ensure_data_dir()
    with open(DATA_MONEY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    user_key = str(user_id)
    return data.get(user_key, {"user_id": user_id, "username": "Unknown", "money": 0})

def get_money_top_users(limit: int = 10) -> list[dict]:
    ensure_data_dir()
    with open(DATA_MONEY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    users = list(data.values())

    users.sort(key=lambda u: (u.get("money", 0)), reverse=True)

    return users[:limit]

def get_all_money_data() -> dict:
    ensure_data_dir()
    with open(DATA_MONEY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
#------------------------ MONEY END ------------------------------------