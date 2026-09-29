import disnake

from utils.slash_commands.sound.mixer import (
    get_sound_files,
    find_sound,
    open_user_mixer,
    play_sound_direct,
)


async def handle_sound_menu(inter: disnake.ApplicationCommandInteraction, bot):
    if not get_sound_files():
        await inter.response.send_message(
            "⚠️ No audio files found in the sound directory.",
            ephemeral=True,
        )
        return

    await open_user_mixer(inter, bot, ephemeral=True)


async def handle_play_named(
    inter: disnake.ApplicationCommandInteraction,
    bot,
    sound_name: str,
):
    file_name = find_sound(sound_name)

    if not file_name:
        await inter.response.send_message(
            f"❌ Sound matching `{sound_name}` was not found.",
            ephemeral=True,
        )
        return

    if not inter.author.voice or not inter.author.voice.channel:
        await inter.response.send_message(
            "⚠️ You must be connected to a voice channel first.",
            ephemeral=True,
        )
        return

    await inter.response.defer(ephemeral=True)

    ok, result = await play_sound_direct(inter, bot, file_name)

    if ok:
        await inter.edit_original_response(
            content=f"▶️ Playing **{result}**."
        )
    else:
        await inter.edit_original_response(content=result)
