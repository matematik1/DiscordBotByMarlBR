import asyncio
import disnake
from disnake.ext import commands

from utils.comands.play.subcom.create_cmd import handle_create_party
from utils.comands.play.subcom.close_cmd import handle_close_room

class PlayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: commands.Context, action: str = None, *args):
        # 1. Меню довідки
        if not action or action.lower() in ("help", "h"):
            embed = disnake.Embed(
                title="🎮 Party Finder & Lobbies",
                description=(
                    "Find teammates and manage temporary voice rooms:\n\n"
                    "• `!play create [game] [mode] [slots] [mmr] [pos]` — Create a lobby\n"
                    "  *(Example: `!play create Dota2 Ranked 5 3000 Pos2`)*\n"
                    "• `!play close` — Delete your current party voice channel\n"
                    "• `!play quick` (or `!p q`) — Quickly create a 5-player Dota 2 lobby"
                ),
                color=disnake.Color.blurple()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)
            return

        act = action.lower()

        # 2. Закриття каналу: !play close
        if act in ("close", "end", "delete"):
            await handle_close_room(ctx)
            return

        # 3. Швидке створення: !play quick
        if act in ("quick", "q"):
            await handle_create_party(ctx, ("Dota 2", "Ranked", 5, "Any", "Any"))
            return

        # 4. Створення лобі: !play create ... або пряме введення гри: !play cs2
        if act in ("create", "c", "start"):
            await handle_create_party(ctx, args)
            return

        # Якщо перший аргумент уже є назвою гри (наприклад, !play dota 5)
        full_args = (action,) + args
        await handle_create_party(ctx, full_args)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        """Автоматично видаляє тимчасовий канал, якщо всі учасники вийшли."""
        channel = before.channel
        if channel and channel.name.startswith("🔊 Party:") and len(channel.members) == 0:
            await asyncio.sleep(30)
            current_channel = member.guild.get_channel(channel.id)
            if current_channel and len(current_channel.members) == 0:
                try:
                    await current_channel.delete(reason="Party room left empty")
                except (disnake.NotFound, disnake.Forbidden):
                    pass

def setup(bot: commands.Bot):
    bot.add_cog(PlayCog(bot))