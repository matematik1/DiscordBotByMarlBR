import sys
import os
import disnake

async def handle_restart(inter: disnake.ApplicationCommandInteraction, bot):
    embed = disnake.Embed(
        title="🔄 Bot Restarting",
        description="Terminating active processes and restarting the application...",
        color=disnake.Color.orange()
    )
    await inter.response.send_message(embed=embed, ephemeral=True)
    
    bot.is_restarting = True
    os.execv(sys.executable, ['python'] + sys.argv)

async def handle_close(inter: disnake.ApplicationCommandInteraction, bot):
    embed = disnake.Embed(
        title="🛑 Bot Shutting Down",
        description="Disconnecting gateway and terminating bot execution.",
        color=disnake.Color.red()
    )
    await inter.response.send_message(embed=embed, ephemeral=True)
    
    await bot.close()