import disnake
from utils.config import LFG_CHANNEL_ID
from utils.slash_commands.play.helpers import (
    JoinVoiceView, 
    get_or_create_voice_channel,
    get_rank_info, 
    create_avatar_with_rank
)

async def handle_create_party(inter: disnake.ApplicationCommandInteraction, game: str, mode: str, slots: int, mmr: str, pos: str):
    await inter.response.defer() # Обов'язково для скілів, що потребують часу (генерація аватарки)

    # 1. Формуємо назву каналу залежно від гри
    if game == "Dota 2":
        voice_base_name = mode
    elif game == "CS2":
        voice_base_name = f"CS {mode}"
    elif game == "Minecraft":
        voice_base_name = f"MC {mode}"
    else:
        voice_base_name = f"{game} {mode}"

    # 2. Створення або пошук голосового каналу
    voice_channel = await get_or_create_voice_channel(inter.guild, voice_base_name)
    
    try:
        await voice_channel.edit(user_limit=slots)
    except disnake.Forbidden:
        pass

    if inter.author.voice and inter.author.voice.channel:
        try:
            await inter.author.move_to(voice_channel)
        except disnake.Forbidden:
            pass

    # 3. Генерація аватарки з рангом (тільки для Dota 2)
    avatar_file = None
    if game == "Dota 2":
        try:
            parsed_mmr = int(mmr) if mmr.isdigit() else 0
            rank_name, rank_file_name = get_rank_info(parsed_mmr)
            
            avatar_buf = await create_avatar_with_rank(inter.author.display_avatar, rank_file_name)
            avatar_file = disnake.File(fp=avatar_buf, filename="ranked_avatar.png")
            
            if mmr.isdigit():
                mmr = f"{mmr} ({rank_name})"
        except Exception as e:
            print(f"Avatar error: {e}")

    # 4. Формування Embed
    embed = disnake.Embed(
        title=f"🎮 Party Finder — {game}",
        description=f"{inter.author.mention} is looking for teammates!",
        color=disnake.Color.blurple()
    )
    
    if avatar_file:
        embed.set_thumbnail(url="attachment://ranked_avatar.png")
    else:
        embed.set_thumbnail(url=inter.author.display_avatar.url)

    embed.add_field(name="🎯 Game Mode", value=f"`{mode}`", inline=True)
    embed.add_field(name="👥 Slots", value=f"`{slots}`", inline=True)
    
    # Не показуємо поле MMR/Позиції для Майнкрафта
    if game != "Minecraft":
        embed.add_field(name="📊 MMR/Rank", value=f"`{mmr}`", inline=True)
        embed.add_field(name="📍 Role", value=f"`{pos}`", inline=True)
        
    embed.add_field(name="🔊 Voice Channel", value=voice_channel.mention, inline=False)
    embed.set_footer(text="Click the voice channel button below to join!")

    # 5. Відправка повідомлення
    join_view = JoinVoiceView(inter.guild.id, voice_channel.id, inter.author.id)
    send_kwargs = {"embed": embed, "view": join_view}
    if avatar_file:
        send_kwargs["file"] = avatar_file

    target_channel = inter.bot.get_channel(LFG_CHANNEL_ID)
    if target_channel:
        await target_channel.send(**send_kwargs)
        if inter.channel.id != target_channel.id:
            await inter.edit_original_response(content=f"✅ Announcement posted in {target_channel.mention}!")
        else:
            await inter.edit_original_response(content="✅ Lobby created!")
    else:
        await inter.edit_original_response(**send_kwargs)