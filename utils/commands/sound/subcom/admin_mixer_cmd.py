from utils.commands.sound.mixer import get_sound_files, open_admin_mixer


async def handle_admin_mixer(ctx, bot):
    if not get_sound_files():
        await ctx.send("⚠️ No audio files found in the sound directory.")
        return

    await open_admin_mixer(ctx, bot, ephemeral=False)
