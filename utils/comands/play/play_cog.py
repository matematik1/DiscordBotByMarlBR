import asyncio
import disnake
from disnake.ext import commands
from utils.config import (
    LFG_CHANNEL_ID, VOICE_CATEGORY_ID, AFK_VOICE_ID, 
    PLAY_SUBCOMMANDS, POSITIONS_MAP
)
from utils.comands.play.helpers import (
    get_or_create_voice_channel, get_rank_info, create_avatar_with_rank
)

class JoinVoiceView(disnake.ui.View):
    def __init__(self, guild_id: int, voice_channel_id: int, creator_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.voice_channel_id = voice_channel_id
        self.creator_id = creator_id
        self.is_locked = False

        voice_url = f"https://discord.com/channels/{guild_id}/{voice_channel_id}"
        self.add_item(
            disnake.ui.Button(
                label="🔊 Join Voice",
                url=voice_url,
                style=disnake.ButtonStyle.link,
                row=0
            )
        )

    async def _check_permissions(self, inter: disnake.MessageInteraction) -> bool:
        is_creator = inter.author.id == self.creator_id
        is_admin = inter.author.guild_permissions.administrator
        if not (is_creator or is_admin):
            await inter.response.send_message(
                "❌ Only the lobby host or an administrator can manage this voice channel!",
                ephemeral=True
            )
            return False
        return True

    @disnake.ui.button(label="➕ +1 Slot", style=disnake.ButtonStyle.primary, row=1)
    async def add_slot_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if not await self._check_permissions(inter):
            return

        channel = inter.guild.get_channel(self.voice_channel_id)
        if not channel:
            await inter.response.send_message("❌ The voice channel no longer exists!", ephemeral=True)
            return

        current_limit = channel.user_limit or len(channel.members)
        if current_limit >= 99:
            await inter.response.send_message("⚠️ Cannot increase slots beyond 99!", ephemeral=True)
            return

        new_limit = current_limit + 1
        try:
            await channel.edit(user_limit=new_limit)
            await inter.response.send_message(f"✅ Voice channel limit increased to **{new_limit}** slots!", ephemeral=True)
        except disnake.Forbidden:
            await inter.response.send_message("❌ Missing permissions to edit voice channel limit.", ephemeral=True)

    @disnake.ui.button(label="🔒 Lock Voice", style=disnake.ButtonStyle.secondary, row=1)
    async def toggle_lock_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if not await self._check_permissions(inter):
            return

        channel = inter.guild.get_channel(self.voice_channel_id)
        if not channel:
            await inter.response.send_message("❌ The voice channel no longer exists!", ephemeral=True)
            return

        self.is_locked = not self.is_locked
        overwrite = channel.overwrites_for(inter.guild.default_role)
        overwrite.connect = False if self.is_locked else None
        await channel.set_permissions(inter.guild.default_role, overwrite=overwrite)

        if self.is_locked:
            button.label = "🔓 Unlock Voice"
            button.style = disnake.ButtonStyle.success
            status_text = "🔒 Voice channel locked for new members!"
        else:
            button.label = "🔒 Lock Voice"
            button.style = disnake.ButtonStyle.secondary
            status_text = "🔓 Voice channel unlocked for everyone!"

        await inter.response.edit_message(view=self)
        await inter.followup.send(status_text, ephemeral=True)

    @disnake.ui.button(label="🛑 End Lobby", style=disnake.ButtonStyle.danger, row=1)
    async def end_lobby_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if not await self._check_permissions(inter):
            return

        await inter.response.defer()

        channel = inter.guild.get_channel(self.voice_channel_id)
        afk_channel = inter.guild.get_channel(AFK_VOICE_ID)

        for item in self.children:
            item.disabled = True

        try:
            await inter.edit_original_response(content="🛑 **Lobby has been closed.**", view=self)
        except Exception:
            pass

        if channel:
            if afk_channel:
                for member in channel.members:
                    try:
                        await member.move_to(afk_channel)
                    except Exception:
                        pass

            try:
                await channel.delete(reason="Lobby ended by host/admin.")
            except Exception:
                pass

        try:
            await inter.followup.send("Voice channel deleted and members moved to AFK.", ephemeral=True)
        except Exception:
            pass

class PlayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        if before.channel is not None and before.channel != after.channel:
            channel = before.channel
            if channel.category_id == VOICE_CATEGORY_ID:
                if len(channel.members) == 0:
                    await asyncio.sleep(60)
                    try:
                        current_channel = member.guild.get_channel(channel.id)
                        if current_channel and len(current_channel.members) == 0:
                            await current_channel.delete(reason="LFG voice channel remained empty for 1 minute.")
                    except Exception:
                        pass

    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, play_contex: str = None, game_type: str = None, mmr: int = 0, pos: int = 0):
        # 1. Якщо аргумент відсутній або запитують допомогу — показуємо актуальний Help
        if play_contex is None or play_contex.lower() in ("help", "h"):
            embed = disnake.Embed(
                title="👥 Party Finder Center",
                description="Create interactive gaming lobbies and gather teammates for matches:",
                color=disnake.Color.green()
            )
            embed.add_field(
                name="• `!play search <mode> <mmr> <pos>` (alias: `!p s`)",
                value=(
                    "> Look for teammates with custom MMR and role.\n"
                    "> **Modes:** `turbo`, `all_pick`, `ranked`, `lp`\n"
                    "> **Roles:** `1`–`5` (or `6` for Any)\n"
                    "> **Example:** `!p s ranked 4500 2`"
                ),
                inline=False
            )
            embed.add_field(
                name="• `!play 1v1` (or `!p 1x1`)",
                value="> Create an instant 1v1 duel challenge room in voice channel",
                inline=False
            )
            embed.add_field(
                name="• Interactive Voice Controls",
                value=(
                    "> 🔊 **Join Voice** — Direct link to join the lobby voice channel\n"
                    "> ➕ **+1 Slot** — Increase max voice room slots\n"
                    "> 🔒 **Lock Voice** — Lock room for non-members\n"
                    "> 🛑 **End Lobby** — Close the party and move users to AFK"
                ),
                inline=False
            )
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )
            await ctx.send(embed=embed)
            return

        action = play_contex.lower()

        # 2. Режим 1v1
        if action in ("1v1", "1x1"):
            mode_title = "Duel (1v1)"
            voice_channel = await get_or_create_voice_channel(ctx.guild, "1x1")
            try:
                await voice_channel.edit(user_limit=2)
            except disnake.Forbidden:
                pass

            if ctx.author.voice and ctx.author.voice.channel:
                try:
                    await ctx.author.move_to(voice_channel)
                except disnake.Forbidden:
                    pass

            embed = disnake.Embed(
                title=f"⚔️ Searching for an opponent — {mode_title}",
                description=f"{ctx.author.mention} is looking for a 1v1 duel opponent!",
                color=disnake.Color.dark_gold()
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.add_field(name="🎯 Game Mode", value=f"`{mode_title}`", inline=True)
            embed.add_field(name="👥 Slots", value="`1 vs 1`", inline=True)
            embed.add_field(name="🔊 Voice Channel", value=voice_channel.mention, inline=False)
            embed.set_footer(text="Click the button below to accept the challenge!")

            join_view = JoinVoiceView(ctx.guild.id, voice_channel.id, ctx.author.id)
            target_channel = self.bot.get_channel(LFG_CHANNEL_ID)
            if target_channel:
                await target_channel.send(embed=embed, view=join_view)
                if ctx.channel.id != target_channel.id:
                    await ctx.send(f"✅ Announcement posted in {target_channel.mention}!", delete_after=5)
            else:
                await ctx.send(embed=embed, view=join_view)
            return

        # 3. Режим пошуку паті (search)
        if action in ("search", "s"):
            if game_type is None or pos not in range(1, 7):
                await ctx.send(
                    "❌ **Invalid parameters!**\n"
                    "Usage: `!play search <mode> <mmr> <pos (1-6)>`\n"
                    "Example: `!p s ranked 4500 2`"
                )
                return

            match game_type.lower():
                case "turbo" | "турбо":
                    mode_title, voice_base, embed_color = "Turbo", "Turbo", disnake.Color.orange()
                case "all_pick" | "алпик" | "аллпик" | "ap" | "unranked":
                    mode_title, voice_base, embed_color = "All Pick (Unranked)", "All Pick", disnake.Color.green()
                case "ranked" | "рейт" | "рейтинг" | "rank":
                    mode_title, voice_base, embed_color = "Ranked Matchmaking", "Ranked", disnake.Color.red()
                case "lp" | "лп" | "low_priority":
                    mode_title, voice_base, embed_color = "Low Priority", "LP", disnake.Color.dark_gray()
                case _:
                    await ctx.send("❌ Unknown game mode! Choose: `turbo`, `all_pick`, `ranked`, or `lp`.")
                    return

            rank_name, rank_file_name = get_rank_info(mmr)

            avatar_file = None
            try:
                avatar_buf = await create_avatar_with_rank(ctx.author.display_avatar, rank_file_name)
                avatar_file = disnake.File(fp=avatar_buf, filename="ranked_avatar.png")
            except Exception as e:
                print(f"Error creating ranked avatar: {e}")

            voice_channel = await get_or_create_voice_channel(ctx.guild, voice_base)

            if ctx.author.voice and ctx.author.voice.channel:
                try:
                    await ctx.author.move_to(voice_channel)
                except disnake.Forbidden:
                    pass

            pos_str = POSITIONS_MAP.get(pos, f"Pos {pos}")
            embed = disnake.Embed(
                title=f"🎮 Party Search — {mode_title}",
                description=f"{ctx.author.mention} is looking for teammates!",
                color=embed_color
            )

            if avatar_file:
                embed.set_thumbnail(url="attachment://ranked_avatar.png")
            else:
                embed.set_thumbnail(url=ctx.author.display_avatar.url)

            embed.add_field(name="🎯 Game Mode", value=f"`{mode_title}`", inline=True)
            embed.add_field(name="📊 MMR & Rank", value=f"`{mmr if mmr > 0 else 'Any'}` ({rank_name})", inline=True)
            embed.add_field(name="📍 Role", value=f"`{pos_str}`", inline=True)
            embed.add_field(name="🔊 Voice Channel", value=voice_channel.mention, inline=False)
            embed.set_footer(text="Click the voice channel button below to join!")

            join_view = JoinVoiceView(ctx.guild.id, voice_channel.id, ctx.author.id)
            target_channel = self.bot.get_channel(LFG_CHANNEL_ID)
            send_files = [avatar_file] if avatar_file else []

            if target_channel:
                await target_channel.send(embed=embed, view=join_view, files=send_files)
                if ctx.channel.id != target_channel.id:
                    await ctx.send(f"✅ Announcement posted in {target_channel.mention}!", delete_after=5)
            else:
                await ctx.send(embed=embed, view=join_view, files=send_files)
            return

        await ctx.send(f"❌ Unknown action `{play_contex}`. Use `!play help` to see available commands.")

def setup(bot: commands.Bot):
    bot.add_cog(PlayCog(bot))