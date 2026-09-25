import asyncio
import disnake
from disnake.ext import commands

from .subcom.create_cmd import handle_create_party
from .subcom.close_cmd import handle_close_room

class PlaySlashCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="play", description="Find teammates and manage gaming lobbies")
    async def play(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @play.sub_command(name="create", description="Create an interactive party lobby")
    async def create(
        self,
        inter: disnake.ApplicationCommandInteraction,
        game: str = commands.Param(
            description="Select game",
            choices=["Dota 2", "Counter-Strike 2", "Valorant", "Deadlock", "Minecraft", "Other"]
        ),
        mode: str = commands.Param(
            default="Ranked",
            description="Game mode (e.g. Ranked, Turbo, Competitive)"
        ),
        slots: int = commands.Param(
            default=5,
            description="Total party size including you (2 to 10)"
        ),
        mmr: str = commands.Param(
            default="Any",
            description="MMR, Rank or Skill level expectation"
        ),
        position: str = commands.Param(
            default="Any",
            description="Required role/position (e.g. Pos 1 / Carry, Mid, Support)"
        )
    ):
        await handle_create_party(inter, game, mode, slots, mmr, position)

    @play.sub_command(name="close", description="Delete the current temporary party voice room")
    async def close(self, inter: disnake.ApplicationCommandInteraction):
        await handle_close_room(inter)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        """Автоматично видаляє тимчасові канали з префіксом '🔊 Party:', якщо всі вийшли."""
        channel = before.channel
        if channel and channel.name.startswith("🔊 Party:") and len(channel.members) == 0:
            # Очікуємо 30 секунд перед видаленням, якщо хтось просто перепідключається
            await asyncio.sleep(30)
            current_channel = member.guild.get_channel(channel.id)
            if current_channel and len(current_channel.members) == 0:
                try:
                    await current_channel.delete(reason="Temporary party channel empty")
                except (disnake.NotFound, disnake.Forbidden):
                    pass