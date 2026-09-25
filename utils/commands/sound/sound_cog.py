import disnake
from disnake.ext import commands

from utils.commands.sound.subcom.user_sound_cmd import handle_sound_menu, handle_play_named
from utils.commands.sound.subcom.stop_cmd import handle_stop_sound

class SoundCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="sound", aliases=["s"])
    async def sound(self, ctx: commands.Context, action: str = None, *args):
        # 1. Помощь
        if action and action.lower() in ("help", "h"):
            embed = disnake.Embed(
                title="🔊 Soundpad & Voice Audio",
                description=(
                    "Play custom sound clips directly in your voice channel:\n\n"
                    "• `!sound` (or `!s`) — Open interactive soundboard menu\n"
                    "• `!sound play <name>` (or `!s <name>`) — Play a specific sound\n"
                    "• `!sound stop` (or `!s stop`) — Stop audio and disconnect bot"
                ),
                color=disnake.Color.teal()
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            await ctx.send(embed=embed)
            return

        # 2. Остановка: !s stop
        if action and action.lower() in ("stop", "leave", "dc"):
            await handle_stop_sound(ctx)
            return

        # 3. Воспроизведение конкретного трека: !s play <название> или !s <название>
        if action and action.lower() in ("play", "p"):
            if not args:
                await ctx.send("❌ Usage: `!sound play <name>`")
                return
            await handle_play_named(ctx, self.bot, args[0])
            return

        if action:
            # Если пользователь сразу ввел название: !s meme
            await handle_play_named(ctx, self.bot, action)
            return

        # 4. Меню по умолчанию: !sound или !s
        await handle_sound_menu(ctx, self.bot)

def setup(bot: commands.Bot):
    bot.add_cog(SoundCog(bot))