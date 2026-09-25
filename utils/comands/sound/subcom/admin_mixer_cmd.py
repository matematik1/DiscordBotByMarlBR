import disnake
from disnake.ext import commands
from utils.comands.sound.mixer import SoundMixerView, get_sound_files

async def handle_admin_mixer(ctx: commands.Context, bot):
    files = get_sound_files()
    if not files:
        await ctx.send("⚠️ No audio files found in sound directory!")
        return

    view = SoundMixerView(
        admin_id=ctx.author.id,
        bot=bot,
        admin_name=ctx.author.display_name,
        admin_avatar_url=ctx.author.display_avatar.url
    )
    await ctx.send(embed=view.build_embed(), view=view)