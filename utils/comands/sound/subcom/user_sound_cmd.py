import disnake
from disnake.ext import commands
from utils.comands.sound.mixer import UserSoundMixerView, get_sound_files

async def handle_sound_menu(ctx: commands.Context, bot):
    files = get_sound_files()
    if not files:
        await ctx.send("⚠️ No audio files found in sound directory!")
        return

    view = UserSoundMixerView(
        user_id=ctx.author.id,
        bot=bot,
        user_name=ctx.author.display_name,
        user_avatar_url=ctx.author.display_avatar.url
    )
    await ctx.send(embed=view.build_embed(), view=view)

async def handle_play_named(ctx: commands.Context, bot, sound_query: str):
    files = get_sound_files()
    match = None
    for f in files:
        if sound_query.lower() in f.lower():
            match = f
            break

    if not match:
        await ctx.send(f"❌ Sound matching `{sound_query}` not found!")
        return

    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("⚠️ You must be connected to a voice channel!")
        return

    view = UserSoundMixerView(
        user_id=ctx.author.id,
        bot=bot,
        user_name=ctx.author.display_name,
        user_avatar_url=ctx.author.display_avatar.url
    )
    msg = await ctx.send(embed=view.build_embed(), view=view)
    
    # Создаем фейковый inter-контекст для вызова метода воспроизведения
    class DummyInteraction:
        def __init__(self, message, author):
            self.author = author
            self.guild = message.guild
            self.response = self
        def is_done(self):
            return True
        async def edit_original_response(self, **kwargs):
            await msg.edit(**kwargs)
        async def send_message(self, *args, **kwargs):
            await ctx.send(*args, **kwargs)

    dummy_inter = DummyInteraction(msg, ctx.author)
    await view.play_sound(dummy_inter, match)