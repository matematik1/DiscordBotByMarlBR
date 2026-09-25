import os
import random
import disnake
from ..mixer import UserSoundMixerView, get_sound_files
from utils.config import SOUND_DIR

async def handle_sound_menu(inter: disnake.ApplicationCommandInteraction, bot):
    files = get_sound_files()
    if not files:
        await inter.response.send_message("⚠️ No audio files found on the server!", ephemeral=True)
        return

    avatar_url = inter.author.display_avatar.url
    view = UserSoundMixerView(
        user_id=inter.author.id,
        bot=bot,
        user_name=inter.author.display_name,
        user_avatar_url=avatar_url
    )
    await inter.response.send_message(embed=view.build_embed(), view=view)

async def handle_play_named(inter: disnake.ApplicationCommandInteraction, bot, sound_name: str):
    files = get_sound_files()
    match = None
    for f in files:
        if sound_name.lower() in f.lower():
            match = f
            break

    if not match:
        await inter.response.send_message(f"❌ Sound matching `{sound_name}` not found!", ephemeral=True)
        return

    avatar_url = inter.author.display_avatar.url
    view = UserSoundMixerView(
        user_id=inter.author.id,
        bot=bot,
        user_name=inter.author.display_name,
        user_avatar_url=avatar_url
    )
    await inter.response.send_message(embed=view.build_embed(), view=view)
    await view.play_sound(inter, match)