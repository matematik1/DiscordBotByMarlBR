import os
import io
import disnake
from PIL import Image
from utils.config import VOICE_CATEGORY_ID, RANG_DIR, AFK_VOICE_ID

async def get_or_create_voice_channel(guild: disnake.Guild, base_name: str) -> disnake.VoiceChannel:
    category = guild.get_channel(VOICE_CATEGORY_ID)
    channels_pool = category.voice_channels if category else guild.voice_channels
    existing_channels = [
        vc for vc in channels_pool 
        if vc.name.lower().startswith(base_name.lower())
    ]

    for vc in existing_channels:
        if len(vc.members) < (vc.user_limit or 5):
            return vc

    channel_number = len(existing_channels) + 1
    new_channel_name = f"{base_name} {channel_number}"

    return await guild.create_voice_channel(
        name=new_channel_name,
        category=category,
        user_limit=5
    )

def get_rank_info(mmr: int):
    if mmr >= 6000:
        return "Immortal", "Titan.png"

    brackets = [
        ("Herald", 1, [0, 150, 300, 460, 610]),
        ("Guardian", 2, [770, 920, 1080, 1230, 1400]),
        ("Crusader", 3, [1540, 1700, 1850, 2000, 2150]),
        ("Archon", 4, [2310, 2450, 2610, 2770, 2930]),
        ("Legend", 5, [3080, 3230, 3390, 3540, 3700]),
        ("Ancient", 6, [3850, 4000, 4150, 4300, 4460]),
        ("Divine", 7, [4620, 4820, 5020, 5220, 5420]),
    ]

    chosen_name = "Herald"
    chosen_rank_id = 1
    chosen_stars = 1

    for title, rank_id, stars_mmr in brackets:
        if mmr >= stars_mmr[0]:
            chosen_name = title
            chosen_rank_id = rank_id
            chosen_stars = 1
            for star_idx, threshold in enumerate(stars_mmr, start=1):
                if mmr >= threshold:
                    chosen_stars = star_idx

    file_name = f"Rank{chosen_rank_id} ({chosen_stars}).png"
    display_title = f"{chosen_name} [{chosen_stars}★]"
    return display_title, file_name

async def create_avatar_with_rank(avatar_asset: disnake.Asset, rank_filename: str) -> io.BytesIO:
    png_avatar = avatar_asset.replace(format="png", size=256)
    avatar_bytes = await png_avatar.read()
    
    avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    base_size = (256, 256)
    if avatar_img.size != base_size:
        avatar_img = avatar_img.resize(base_size, Image.Resampling.LANCZOS)

    rank_path = os.path.join(RANG_DIR, rank_filename)
    if os.path.exists(rank_path):
        rank_img = Image.open(rank_path).convert("RGBA")
        rank_w = int(base_size[0] * 0.45)
        w_percent = rank_w / float(rank_img.size[0])
        rank_h = int(float(rank_img.size[1]) * float(w_percent))
        rank_img = rank_img.resize((rank_w, rank_h), Image.Resampling.LANCZOS)

        pos_x = base_size[0] - rank_w
        pos_y = 0
        avatar_img.paste(rank_img, (pos_x, pos_y), mask=rank_img)

    out_buffer = io.BytesIO()
    avatar_img.save(out_buffer, format="PNG")
    out_buffer.seek(0)
    return out_buffer

class JoinVoiceView(disnake.ui.View):
    def __init__(self, guild_id: int, voice_channel_id: int, creator_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.voice_channel_id = voice_channel_id
        self.creator_id = creator_id
        self.is_locked = False

        voice_url = f"https://discord.com/channels/{guild_id}/{voice_channel_id}"
        self.add_item(disnake.ui.Button(label="🔊 Join Voice", url=voice_url, style=disnake.ButtonStyle.link, row=0))

    async def _check_permissions(self, inter: disnake.MessageInteraction) -> bool:
        if inter.author.id != self.creator_id and not inter.author.guild_permissions.administrator:
            await inter.response.send_message("❌ Only the lobby host or an admin can manage this room!", ephemeral=True)
            return False
        return True

    @disnake.ui.button(label="➕ +1 Slot", style=disnake.ButtonStyle.primary, row=1)
    async def add_slot_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if not await self._check_permissions(inter): return
        channel = inter.guild.get_channel(self.voice_channel_id)
        if not channel:
            await inter.response.send_message("❌ Channel no longer exists!", ephemeral=True)
            return
        new_limit = min((channel.user_limit or len(channel.members)) + 1, 99)
        try:
            await channel.edit(user_limit=new_limit)
            await inter.response.send_message(f"✅ Slot added! Max: {new_limit}", ephemeral=True)
        except disnake.Forbidden:
            await inter.response.send_message("❌ Permission denied.", ephemeral=True)

    @disnake.ui.button(label="🔒 Lock Voice", style=disnake.ButtonStyle.secondary, row=1)
    async def toggle_lock_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if not await self._check_permissions(inter): return
        channel = inter.guild.get_channel(self.voice_channel_id)
        if not channel:
            await inter.response.send_message("❌ Channel no longer exists!", ephemeral=True)
            return

        self.is_locked = not self.is_locked
        overwrite = channel.overwrites_for(inter.guild.default_role)
        overwrite.connect = False if self.is_locked else None
        await channel.set_permissions(inter.guild.default_role, overwrite=overwrite)

        button.label = "🔓 Unlock Voice" if self.is_locked else "🔒 Lock Voice"
        button.style = disnake.ButtonStyle.success if self.is_locked else disnake.ButtonStyle.secondary
        await inter.response.edit_message(view=self)
        await inter.followup.send("🔒 Voice locked!" if self.is_locked else "🔓 Voice unlocked!", ephemeral=True)

    @disnake.ui.button(label="🛑 End Lobby", style=disnake.ButtonStyle.danger, row=1)
    async def end_lobby_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if not await self._check_permissions(inter): return
        await inter.response.defer()
        channel = inter.guild.get_channel(self.voice_channel_id)
        afk_channel = inter.guild.get_channel(AFK_VOICE_ID)

        for item in self.children: item.disabled = True
        try: await inter.edit_original_response(content="🛑 **Lobby has been closed.**", view=self)
        except Exception: pass

        if channel:
            if afk_channel:
                for member in channel.members:
                    try: await member.move_to(afk_channel)
                    except Exception: pass
            try: await channel.delete(reason="Lobby ended by host.")
            except Exception: pass