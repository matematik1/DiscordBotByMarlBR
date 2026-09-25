import os
import io
import disnake
from PIL import Image
from utils.config import VOICE_CATEGORY_ID, RANG_DIR

async def get_or_create_voice_channel(guild: disnake.Guild, base_name: str) -> disnake.VoiceChannel:
    category = guild.get_channel(VOICE_CATEGORY_ID)
    channels_pool = category.voice_channels if category else guild.voice_channels
    existing_channels = [
        vc for vc in channels_pool 
        if vc.name.lower().startswith(base_name.lower())
    ]

    for vc in existing_channels:
        if len(vc.members) < (vc.user_limit or 5):
            return vc

    channel_number = len(existing_channels) + 1
    new_channel_name = f"{base_name} {channel_number}"

    return await guild.create_voice_channel(
        name=new_channel_name,
        category=category,
        user_limit=5
    )

def get_rank_info(mmr: int):
    if mmr >= 6000:
        return "Immortal", "Titan.png"

    brackets = [
        ("Herald", 1, [0, 150, 300, 460, 610]),
        ("Guardian", 2, [770, 920, 1080, 1230, 1400]),
        ("Crusader", 3, [1540, 1700, 1850, 2000, 2150]),
        ("Archon", 4, [2310, 2450, 2610, 2770, 2930]),
        ("Legend", 5, [3080, 3230, 3390, 3540, 3700]),
        ("Ancient", 6, [3850, 4000, 4150, 4300, 4460]),
        ("Divine", 7, [4620, 4820, 5020, 5220, 5420]),
    ]

    chosen_name = "Herald"
    chosen_rank_id = 1
    chosen_stars = 1

    for title, rank_id, stars_mmr in brackets:
        if mmr >= stars_mmr[0]:
            chosen_name = title
            chosen_rank_id = rank_id
            chosen_stars = 1
            for star_idx, threshold in enumerate(stars_mmr, start=1):
                if mmr >= threshold:
                    chosen_stars = star_idx

    file_name = f"Rank{chosen_rank_id} ({chosen_stars}).png"
    display_title = f"{chosen_name} [{chosen_stars}★]"
    return display_title, file_name

async def create_avatar_with_rank(avatar_asset: disnake.Asset, rank_filename: str) -> io.BytesIO:
    png_avatar = avatar_asset.replace(format="png", size=256)
    avatar_bytes = await png_avatar.read()
    
    avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    base_size = (256, 256)
    if avatar_img.size != base_size:
        avatar_img = avatar_img.resize(base_size, Image.Resampling.LANCZOS)

    rank_path = os.path.join(RANG_DIR, rank_filename)
    if os.path.exists(rank_path):
        rank_img = Image.open(rank_path).convert("RGBA")

        rank_w = int(base_size[0] * 0.45)
        w_percent = rank_w / float(rank_img.size[0])
        rank_h = int(float(rank_img.size[1]) * float(w_percent))
        rank_img = rank_img.resize((rank_w, rank_h), Image.Resampling.LANCZOS)

        pos_x = base_size[0] - rank_w
        pos_y = 0
        avatar_img.paste(rank_img, (pos_x, pos_y), mask=rank_img)
    else:
        print(f"[WARNING] Файл рангу не знайдено: {os.path.abspath(rank_path)}")

    out_buffer = io.BytesIO()
    avatar_img.save(out_buffer, format="PNG")
    out_buffer.seek(0)
    return out_buffer