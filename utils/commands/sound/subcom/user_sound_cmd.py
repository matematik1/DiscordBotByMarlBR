from utils.commands.sound.mixer import (
    get_sound_files,
    find_sound,
    open_user_mixer,
    play_sound_direct,
)


async def handle_sound_menu(ctx, bot):
    if not get_sound_files():
        await ctx.send("⚠️ No audio files found in the sound directory.")
        return

    await open_user_mixer(ctx, bot)


async def handle_play_named(ctx, bot, sound_query: str):
    file_name = find_sound(sound_query)

    if not file_name:
        await ctx.send(
            f"❌ Sound matching `{sound_query}` was not found."
        )
        return

    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("⚠️ You must be connected to a voice channel first.")
        return

    ok, result = await play_sound_direct(ctx, bot, file_name)

    if not ok:
        await ctx.send(result)
        return

    await ctx.send(
        f"▶️ Playing **{result}**.",
        delete_after=4,
    )
