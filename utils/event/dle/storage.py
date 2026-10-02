import json
import os
from zoneinfo import ZoneInfo
from datetime import datetime

DLE_HERO_FILE = os.path.join("data", "dle_hero.json")

def current_date() -> str:
    now = datetime.now(ZoneInfo("Europe/Kyiv"))
    return now.date().isoformat()

def ensure_data_dir():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DLE_HERO_FILE):
        with open(DLE_HERO_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def get_current_hero() -> dict | None:
    ensure_data_dir()
    with open(DLE_HERO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("current_hero")

def get_daly_date() -> str:
    ensure_data_dir()
    with open(DLE_HERO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("date")

def save_current_hero(hero_id: int, hero_name: str):
    ensure_data_dir()
    with open(DLE_HERO_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    data["current_hero"] = {
        "hero_id": hero_id,
        "hero_name": hero_name,
        "date": current_date()
    }

    with open(DLE_HERO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
