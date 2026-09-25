import asyncio
import disnake

class LobbyView(disnake.ui.View):
    def __init__(self, leader: disnake.Member, game: str, mode: str, max_slots: int, target_mmr: str, position: str):
        super().__init__(timeout=600)  # Лобі живе 10 хвилин
        self.leader = leader
        self.game = game
        self.mode = mode
        self.max_slots = max_slots
        self.target_mmr = target_mmr
        self.position = position
        
        self.members: list[disnake.Member] = [leader]
        self.temp_voice_channel: disnake.VoiceChannel | None = None

    def build_embed(self) -> disnake.Embed:
        member_list = "\n".join([f"• {m.mention} ({m.display_name})" for m in self.members])
        empty_slots = self.max_slots - len(self.members)
        if empty_slots > 0:
            member_list += f"\n*+ {empty_slots} slot(s) remaining...*"

        embed = disnake.Embed(
            title=f"🎮 Party Finder — {self.game.upper()}",
            description=(
                f"**Leader:** {self.leader.mention}\n"
                f"**Game Mode:** `{self.mode}`\n"
                f"**Target MMR/Rank:** `{self.target_mmr}`\n"
                f"**Required Position/Role:** `{self.position}`\n\n"
                f"👥 **Party Members ({len(self.members)}/{self.max_slots}):**\n"
                f"{member_list}"
            ),
            color=disnake.Color.blurple()
        )
        embed.set_thumbnail(url=self.leader.display_avatar.url)
        embed.set_footer(text="Click 'Join Party' below to hop in! • Expires in 10 minutes")
        return embed

    @disnake.ui.button(label="Join Party", style=disnake.ButtonStyle.success, emoji="➕")
    async def join_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id in [m.id for m in self.members]:
            await inter.response.send_message("⚠️ You are already in this party!", ephemeral=True)
            return

        if len(self.members) >= self.max_slots:
            await inter.response.send_message("❌ This party is already full!", ephemeral=True)
            return

        self.members.append(inter.author)
        await inter.response.edit_message(embed=self.build_embed(), view=self)

        # Коли паті повне — створюємо тимчасовий войс
        if len(self.members) == self.max_slots:
            await self._create_temporary_voice(inter.guild)

    @disnake.ui.button(label="Leave", style=disnake.ButtonStyle.secondary, emoji="➖")
    async def leave_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id == self.leader.id:
            await inter.response.send_message("❌ The leader cannot leave! Use 'Disband' instead.", ephemeral=True)
            return

        if inter.author.id not in [m.id for m in self.members]:
            await inter.response.send_message("⚠️ You are not in this party!", ephemeral=True)
            return

        self.members = [m for m in self.members if m.id != inter.author.id]
        await inter.response.edit_message(embed=self.build_embed(), view=self)

    @disnake.ui.button(label="Disband", style=disnake.ButtonStyle.danger, emoji="🗑️")
    async def disband_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id != self.leader.id and not inter.author.guild_permissions.administrator:
            await inter.response.send_message("❌ Only the party leader can disband this party!", ephemeral=True)
            return

        self.stop()
        for child in self.children:
            child.disabled = True

        embed = disnake.Embed(
            title="🚫 Party Disbanded",
            description=f"The party was closed by {inter.author.mention}.",
            color=disnake.Color.dark_gray()
        )
        await inter.response.edit_message(embed=embed, view=self)

    async def _create_temporary_voice(self, guild: disnake.Guild):
        category = self.leader.voice.channel.category if (self.leader.voice and self.leader.voice.channel) else None
        channel_name = f"🔊 Party: {self.game.title()}"
        
        try:
            self.temp_voice_channel = await guild.create_voice_channel(
                name=channel_name,
                category=category,
                user_limit=self.max_slots,
                reason="Temporary party voice channel"
            )
        except disnake.Forbidden:
            pass