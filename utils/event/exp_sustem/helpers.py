from utils.config import XP_INTERCASE, BASE_XP

def get_exp_for_lvl(lvl: int) -> int:
    base_xp = BASE_XP
    increase = XP_INTERCASE
    user_lvl = lvl

    return int((base_xp + (lvl * base_xp) + (2 * lvl) + (2 * lvl * increase) - 2) // 5)

def check_level_up(xp: int, current_lvl: int) -> tuple[int, int, bool]:
    user_xp = xp
    user_lvl = current_lvl
    initial_lvl = current_lvl

    while user_xp >= get_exp_for_lvl(user_lvl):
        user_xp -= get_exp_for_lvl(user_lvl)
        user_lvl += 1

    while user_xp < 0 and user_lvl > 1:
        user_lvl -= 1
        user_xp += get_exp_for_lvl(user_lvl)

    if user_lvl == 1 and user_xp < 0:
        user_xp = 0

    did_level_change = user_lvl != initial_lvl
    return user_xp, user_lvl, did_level_change

def create_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Генерує текстовий прогрес-бар (наприклад: ▰▰▰▰▱▱▱▱▱▱)."""
    if total <= 0:
        return "▱" * length
    ratio = min(max(current / total, 0.0), 1.0)
    filled_len = int(round(length * ratio))
    return "▰" * filled_len + "▱" * (length - filled_len)