import disnake
from ..mixer import SoundMixerView, get_sound_files

async def handle_admin_mixer(inter: disnake.ApplicationCommandInteraction, bot):
    files = get_sound_files()
    if not files:
        await inter.response.send_message("⚠️ No audio files found in sound directory!", ephemeral=True)
        return

    avatar_url = inter.author.display_avatar.url
    view = SoundMixerView(
        admin_id=inter.author.id,
        bot=bot,
        admin_name=inter.author.display_name,
        admin_avatar_url=avatar_url
    )
    await inter.response.send_message(embed=view.build_embed(), view=view, ephemeral=True)