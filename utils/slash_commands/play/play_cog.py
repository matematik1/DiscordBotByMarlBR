import asyncio
import disnake
from disnake.ext import commands
from utils.slash_commands.play.subcom.create_cmd import handle_create_party
from utils.slash_commands.play.subcom.close_cmd import handle_close_room
from utils.config import VOICE_CATEGORY_ID

class PlaySlashCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="play", description="Party Finder and Lobby Controls")
    async def play(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @play.sub_command(name="create", description="Create a custom gaming lobby")
    async def create(
        self, 
        inter: disnake.ApplicationCommandInteraction,
        game: str = commands.Param(
            choices=["Dota 2", "CS2", "Minecraft"], 
            description="Select the game"
        ),
        mode: str = commands.Param(
            default="All Pick", 
            choices=[
                "All Pick", "Ranked", "Turbo", "Ability Draft", 
                "Premier (CS2)", "Competitive (CS2)", "Wingman (CS2)", 
                "Survival (MC)", "Mini-games (MC)", "Any / Other"
            ],
            description="Game mode"
        ),
        slots: int = commands.Param(
            default=5, 
            choices=[2, 3, 4, 5, 10], 
            description="Number of players"
        ),
        mmr: str = commands.Param(
            default="Any", 
            choices=[
                "Any", 
                "Herald / Guardian", "Crusader / Archon", 
                "Legend / Ancient", "Divine / Immortal", 
                "Silver / Gold (CS2)", "MG / Global (CS2)", 
                "Faceit 1-5", "Faceit 6-10"
            ],
            description="Required MMR/Rank"
        ),
        pos: str = commands.Param(
            default="Any", 
            choices=[
                "Any", 
                "Pos 1 (Carry)", "Pos 2 (Mid)", "Pos 3 (Offlane)", 
                "Pos 4 (Soft Supp)", "Pos 5 (Hard Supp)", 
                "Sniper / AWP (CS2)", "IGL / Captain"
            ],
            description="Required Position/Role"
        )
    ):
        await handle_create_party(inter, game, mode, slots, mmr, pos)

    @play.sub_command(name="quick", description="Instantly create a 5-player Dota 2 All Pick lobby")
    async def quick(self, inter: disnake.ApplicationCommandInteraction):
        await handle_create_party(inter, "Dota 2", "All Pick", 5, "Any", "Any")

    @play.sub_command(name="close", description="Delete your current party voice channel")
    async def close(self, inter: disnake.ApplicationCommandInteraction):
        await handle_close_room(inter)

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
    bot.add_cog(PlaySlashCog(bot))