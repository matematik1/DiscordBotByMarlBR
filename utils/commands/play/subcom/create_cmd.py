import disnake
from disnake.ext import commands
from utils.config import LFG_CHANNEL_ID
from utils.commands.play.helpers import (
    JoinVoiceView, 
    get_or_create_voice_channel,
    get_rank_info, 
    create_avatar_with_rank
)

async def handle_create_party(ctx: commands.Context, args: tuple):
    game = "Dota 2"
    mode = "All Pick"
    slots = 5
    mmr = "Any"
    pos = "Any"

    if len(args) >= 1:
        game = args[0]
    if len(args) >= 2:
        mode = args[1]
    if len(args) >= 3:
        try:
            slots = int(args[2])
            if slots < 2 or slots > 10:
                slots = 5
        except ValueError:
            pos = args[2]
    if len(args) >= 4:
        mmr = args[3]
    if len(args) >= 5:
        pos = args[4]

    # 1. Створення або пошук голосового каналу
    voice_base_name = f"{game} {mode}" if mode != "All Pick" else mode
    voice_channel = await get_or_create_voice_channel(ctx.guild, voice_base_name)
    
    try:
        await voice_channel.edit(user_limit=slots)
    except disnake.Forbidden:
        pass

    if ctx.author.voice and ctx.author.voice.channel:
        try:
            await ctx.author.move_to(voice_channel)
        except disnake.Forbidden:
            pass

    # 2. Генерація аватарки з рангом
    avatar_file = None
    if "dota" in game.lower() or "дота" in game.lower():
        try:
            parsed_mmr = int(mmr) if mmr.isdigit() else 0
            rank_name, rank_file_name = get_rank_info(parsed_mmr)
            
            avatar_buf = await create_avatar_with_rank(ctx.author.display_avatar, rank_file_name)
            avatar_file = disnake.File(fp=avatar_buf, filename="ranked_avatar.png")
            
            if mmr.isdigit():
                mmr = f"{mmr} ({rank_name})"
        except Exception as e:
            print(f"Avatar error: {e}")

    # 3. Формування Embed
    embed = disnake.Embed(
        title=f"🎮 Party Finder — {game.title()}",
        description=f"{ctx.author.mention} is looking for teammates!",
        color=disnake.Color.blurple()
    )
    
    if avatar_file:
        embed.set_thumbnail(url="attachment://ranked_avatar.png")
    else:
        embed.set_thumbnail(url=ctx.author.display_avatar.url)

    embed.add_field(name="🎯 Game Mode", value=f"`{mode}`", inline=True)
    embed.add_field(name="👥 Slots", value=f"`{slots}`", inline=True)
    embed.add_field(name="📊 MMR & Rank", value=f"`{mmr}`", inline=True)
    embed.add_field(name="📍 Role", value=f"`{pos}`", inline=True)
    embed.add_field(name="🔊 Voice Channel", value=voice_channel.mention, inline=False)
    embed.set_footer(text="Click the voice channel button below to join!")

    # 4. Відправка повідомлення з кнопками управління лобі
    join_view = JoinVoiceView(ctx.guild.id, voice_channel.id, ctx.author.id)
    send_kwargs = {"embed": embed, "view": join_view}
    if avatar_file:
        send_kwargs["file"] = avatar_file

    target_channel = ctx.bot.get_channel(LFG_CHANNEL_ID)
    if target_channel:
        await target_channel.send(**send_kwargs)
        if ctx.channel.id != target_channel.id:
            await ctx.send(f"✅ Announcement posted in {target_channel.mention}!", delete_after=5)
    else:
        await ctx.send(**send_kwargs)