import disnake
from disnake.ext import commands

async def handle_restart(ctx: commands.Context, bot: commands.Bot):
    embed = disnake.Embed(
        title="🔄 Bot Restarting",
        description="Terminating active processes and restarting the application...",
        color=disnake.Color.orange()
    )
    await ctx.send(embed=embed, delete_after=5)
    
    # Примусове відключення від голосового каналу
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.disconnect(force=True)
        
    print("Bot start restart command")
    bot.is_restarting = True
    await bot.close()  # Закриваємо сесію, далі main.py зробить свою справу

async def handle_close(ctx: commands.Context, bot: commands.Bot):
    embed = disnake.Embed(
        title="🛑 Bot Shutting Down",
        description="Disconnecting gateway and terminating bot execution.",
        color=disnake.Color.red()
    )
    await ctx.send(embed=embed, delete_after=5)
    
    # Примусове відключення від голосового каналу
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.disconnect(force=True)
        
    print("Bot close!")
    bot.is_restarting = False
    await bot.close()