import asyncio
import disnake
from disnake.ext import commands
from utils.commands.play.subcom.create_cmd import handle_create_party
from utils.commands.play.subcom.close_cmd import handle_close_room
from utils.config import VOICE_CATEGORY_ID

class PlayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name="play", aliases=["p"], invoke_without_command=True)
    async def play(self, ctx: commands.Context, action: str = None, *args):
        if not action or action.lower() in ("help", "h"):
            embed = disnake.Embed(
                title="🎮 Party Finder & Lobbies",
                description=(
                    "Find teammates and manage temporary voice rooms:\n\n"
                    "• `!play create [game] [mode] [slots] [mmr] [pos]` — Create a lobby\n"
                    "  *(Example: `!play create Dota2 Ranked 5 3000 Pos2`)*\n"
                    "• `!play close` — Delete your current party voice channel\n"
                    "• `!play quick` (or `!p q`) — Quickly create a 5-player Dota 2 All Pick lobby"
                ),
                color=disnake.Color.blurple()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)
            return

        act = action.lower()

        if act in ("close", "end", "delete"):
            await handle_close_room(ctx)
            return

        if act in ("quick", "q"):
            await handle_create_party(ctx, ("Dota 2", "All Pick", 5, "Any", "Any"))
            return

        if act in ("create", "c", "start"):
            await handle_create_party(ctx, args)
            return

        full_args = (action,) + args
        await handle_create_party(ctx, full_args)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        channel = before.channel
        if channel and channel.category_id == VOICE_CATEGORY_ID and len(channel.members) == 0:
            await asyncio.sleep(60)
            current_channel = member.guild.get_channel(channel.id)
            if current_channel and len(current_channel.members) == 0:
                try:
                    await current_channel.delete(reason="Party room left empty for 1 minute")
                except (disnake.NotFound, disnake.Forbidden):
                    pass

def setup(bot: commands.Bot):
    bot.add_cog(PlayCog(bot))