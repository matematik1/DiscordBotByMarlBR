import sys
import os
import disnake
from disnake.ext import commands

async def handle_restart(ctx: commands.Context, bot):
    embed = disnake.Embed(
        title="🔄 Bot Restarting",
        description="Terminating active tasks and reloading the process...",
        color=disnake.Color.orange()
    )
    await ctx.send(embed=embed)
    bot.is_restarting = True
    os.execv(sys.executable, ['python'] + sys.argv)

async def handle_close(ctx: commands.Context, bot):
    embed = disnake.Embed(
        title="🛑 Bot Shutting Down",
        description="Disconnecting gateway and safely terminating execution.",
        color=disnake.Color.red()
    )
    await ctx.send(embed=embed)
    await bot.close()