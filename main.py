import disnake
from disnake.ext import commands
import asyncio
import os
import sys
import subprocess
import random
import io
from PIL import Image
import urllib.parse

bot = commands.Bot(command_prefix="!", intents=disnake.Intents.all(), help_command=None)

embed_color = disnake.Color.dark_theme()
SOUND_DIR = "soundboard"
HEROES_GIF_DIR = os.path.join("video", "heroes")
ITEMS_B_DIR = os.path.join("img", "items", "b")
ITEMS_I_DIR = os.path.join("img", "items", "i")
RANG_DIR = os.path.join("img", "rang")
LFG_CHANNEL_ID = 1552413792795889745
VOICE_CATEGORY_ID = 1552388769649393774
AFK_VOICE_ID = 1552406299130728559

DOTA_POSITIONS = [
    "Pos 1 (Safe Lane Carry)", 
    "Pos 2 (Mid Lane)", 
    "Pos 3 (Offlane)", 
    "Pos 4 (Soft Support)", 
    "Pos 5 (Hard Support)",
    "Pos 6 (Лесничок)"
]

POSITIONS_MAP = {
    1: "Pos 1 (Carry)",
    2: "Pos 2 (Mid)",
    3: "Pos 3 (Offlane)",
    4: "Pos 4 (Soft Support)",
    5: "Pos 5 (Hard Support)",
    6: "Pos 6 (Jungler / Roamer)"
}

HERO_NAME_OVERRIDES = {
    "nevermore": "Shadow Fiend",
    "zuus": "Zeus",
    "windrunner": "Windranger",
    "shredder": "Timbersaw",
    "rattletrap": "Clockwerk",
    "skeleton_king": "Wraith King",
    "wisp": "Io",
    "obsidian_destroyer": "Outworld Destroyer",
    "furion": "Nature's Prophet",
    "abyssal_underlord": "Underlord",
    "magnataur": "Magnus",
    "treant": "Treant Protector",
    "vengefulspirit": "Vengeful Spirit",
    "queenofpain": "Queen of Pain",
    "doom_bringer": "Doom",
    "necrolyte": "Necrophos",
}

FFMPEG_OPTIONS = {
    "before_options": "-nostdin",
    "options": "-vn -af loudnorm=I=-16:TP=-1.5:LRA=11"
}

DOTA_GUILD_INFO = {
    "name": "MarlB0ro",
    "tag": "MarBR",
    "leader_dota_id": "1257746704",
    "leader_name": "Laimer",
    "leader_steam": "https://steamcommunity.com/profiles/76561199218012432",
    "officer_name": "Majjis",
    "officer_steam": "https://steamcommunity.com/id/majjis_twink"
}

PLAY_SUBCOMMANDS = {
    "search": "Create a team search announcement \n(`!p s <mode> <mmr> <pos>`)",
    "1x1 / 1v1": "Creates a voice channel for the duel",
    "help": "Displays this menu"
}

SUBCOMMANDS = {
    "sound (s)": "Plays sounds in your voice channel",
    "dota (d)": "Dota-related commands",
    "play (p)": "Finding teammates and duels",
    "help (h)": "Dislays this menu"
}

DOTA_SUBCOMMANDS = {
    "guild": "Information and links to the guild in DotA",
    "random": "Random hero position and build",
    "hero": "Random hero with direct tracker links",
    "meta": "Current Dota 2 meta overview and tracker links",
    "help": "Displays this menu"
}

SOUND_SUBCOMMANDS = {
    "stop": "Stoped sound",
    "list": "Displays the names of all sounds.",
    "help": "Displays this menu"
}

ADM_SUBCOMMANDS = {
    "restart": "Restarting the bot",
    "close": "Closing the bot",
    "clear": "Clearing chat messages",
    "help": "Displays this menu"
}

bot.is_restarting = False

def get_available_heroes():
    if not os.path.exists(HEROES_GIF_DIR):
        return []

    heroes = []
    prefix_double = "npc_dota_hero_npc_dota_hero_"
    prefix_single = "npc_dota_hero_"

    for filename in os.listdir(HEROES_GIF_DIR):
        if filename.lower().endswith(".gif"):
            clean_name = filename[:-4]

            if clean_name.startswith(prefix_double):
                clean_name = clean_name[len(prefix_double):]
            elif clean_name.startswith(prefix_single):
                clean_name = clean_name[len(prefix_single):]

            if clean_name in HERO_NAME_OVERRIDES:
                display_name = HERO_NAME_OVERRIDES[clean_name]
            else:
                display_name = clean_name.replace("_", " ").title()

            d2pt_slug = urllib.parse.quote(display_name)

            clean_dotabuff = display_name.lower().replace("'", "").replace(" ", "-")

            heroes.append({
                "name": display_name,
                "d2pt_slug": d2pt_slug,
                "dotabuff_slug": clean_dotabuff,
                "file_path": os.path.join(HEROES_GIF_DIR, filename),
                "file_name": filename
            })

    return heroes

def generate_inventory_image(boot_num: int, item_nums: list[int]) -> io.BytesIO:
    image_paths = [os.path.join(ITEMS_B_DIR, f"{boot_num}.png")]
    for num in item_nums:
        image_paths.append(os.path.join(ITEMS_I_DIR, f"{num}.png"))

    images = [Image.open(path).convert("RGBA") for path in image_paths]

    target_height = 80
    resized_images = []
    for img in images:
        w_percent = target_height / float(img.size[1])
        new_width = int(float(img.size[0]) * float(w_percent))
        resized_images.append(img.resize((new_width, target_height), Image.Resampling.LANCZOS))

    padding = 10
    total_width = sum(img.size[0] for img in resized_images) + padding * (len(resized_images) - 1)
    total_height = target_height

    inventory_canvas = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

    current_x = 0
    for img in resized_images:
        inventory_canvas.paste(img, (current_x, 0), img)
        current_x += img.size[0] + padding

    buffer = io.BytesIO()
    inventory_canvas.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

class DotaLinksView(disnake.ui.View):
    def __init__(self, d2pt_slug: str = None, dotabuff_slug: str = None):
        super().__init__(timeout=None)
        
        if d2pt_slug and dotabuff_slug:
            self.d2pt_url = f"https://dota2protracker.com/hero/{d2pt_slug}"
            self.dotabuff_url = f"https://www.dotabuff.com/heroes/{dotabuff_slug}"
        else:
            self.d2pt_url = "https://dota2protracker.com/meta"
            self.dotabuff_url = "https://www.dotabuff.com/heroes/meta"

    @disnake.ui.button(label="Dota2ProTracker", style=disnake.ButtonStyle.primary, emoji="📊")
    async def protracker_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message(
            f"📊 **Dota2ProTracker:** {self.d2pt_url}", 
            ephemeral=True
        )

    @disnake.ui.button(label="Dotabuff", style=disnake.ButtonStyle.danger, emoji="📈")
    async def dotabuff_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message(
            f"📈 **Dotabuff:** {self.dotabuff_url}", 
            ephemeral=True
        )

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
        """Checks if the user is the lobby creator or has administrator rights."""
        is_creator = inter.author.id == self.creator_id
        is_admin = inter.author.guild_permissions.administrator
        if not (is_creator or is_admin):
            await inter.response.send_message(
                "❌ Only the lobby host or an administrator can manage this voice channel!",
                ephemeral=True
            )
            return False
        return True

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
                    except disnake.Forbidden:
                        pass
                    except Exception:
                        pass

            try:
                await channel.delete(reason="Lobby ended by host/admin.")
            except disnake.Forbidden:
                pass
            except Exception:
                pass

        try:
            await inter.followup.send("Voice channel deleted and members moved to AFK.", ephemeral=True)
        except Exception:
            pass

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

    file_name = f"Rank{chosen_rank_id}_{chosen_stars}.png"
    display_title = f"{chosen_name} [{chosen_stars}★]"
    return display_title, file_name

async def create_avatar_with_rank(avatar_asset: disnake.Asset, rank_filename: str) -> io.BytesIO:
    avatar_bytes = await avatar_asset.read()
    avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")

    base_size = (256, 256)
    avatar_img = avatar_img.resize(base_size, Image.Resampling.LANCZOS)

    rank_path = os.path.join(RANG_DIR, rank_filename)
    if os.path.exists(rank_path):
        rank_img = Image.open(rank_path).convert("RGBA")

        rank_w = int(base_size[0] * 0.45)
        w_percent = rank_w / float(rank_img.size[0])
        rank_h = int(float(rank_img.size[1]) * float(w_percent))
        rank_img = rank_img.resize((rank_w, rank_h), Image.Resampling.LANCZOS)

        pos_x = base_size[0] - rank_w + 5
        pos_y = -5
        avatar_img.paste(rank_img, (pos_x, pos_y), rank_img)

    out_buffer = io.BytesIO()
    avatar_img.save(out_buffer, format="PNG")
    out_buffer.seek(0)
    return out_buffer

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.event
async def on_member_join(member):
    role = member.guild.get_role(1543689985981546587)
   
    if role is not None:
        await member.add_roles(role)
        print(f'Given role {role.name} to {member.name}')
    else:
        print(f'Role not found in guild {member.guild.name}')

@bot.command(aliases=["s"])
async def sound(ctx: commands.Context, sound_name: str = None):
    if sound_name and sound_name.lower() in ("help", "h"):
        commands_list = "\n".join(
            f"• `!sound {name}` — {desc}"
            for name, desc in SOUND_SUBCOMMANDS.items()
        )

        message = (
            "**Available subcommands for `!sound`**\n"
            f"{commands_list}\n"
            "• `!sound <SOUND NAME>` - Play the selected sound in the voice channel"
        )

        await ctx.send(message)
        return
    
    if sound_name and sound_name.lower() in ("list", "l"):
        if not os.path.exists(SOUND_DIR):
            await ctx.send("DIR NOT FOUND")
            return

        sounds = [
            file[:-4] for file in os.listdir(SOUND_DIR)
            if file.lower().endswith(".mp3")
        ]

        if not sounds:
            await ctx.send("SOUND NOT FOUND")
            return

        sound_list_text = "\n".join(f"- `{name}`" for name in sorted(sounds))

        await ctx.send(f'ALL SOUND: \n{sound_list_text}')
        return

    if sound_name and sound_name.lower() in ("stop", "s"):
        voice_client: disnake.VoiceClient = ctx.voice_client
        if voice_client and voice_client.is_connected():
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            print("Sound Stoped")
        return

    if sound_name is None:
        await ctx.send("WRITE SOUND NAME")
        return

    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("YOU NEED TO BE IN A VOICE CHANNEL")
        return

    target_channel = ctx.author.voice.channel

    if not sound_name.endswith(".mp3"):
        sound_name += ".mp3"

    file_path = os.path.join(SOUND_DIR, sound_name)

    if not os.path.exists(file_path):
        await ctx.send("SOUND NOT FOUND")
        return
    
    voice_client: disnake.VoiceClient = ctx.voice_client

    if voice_client is None:
        voice_client = await target_channel.connect()
    elif voice_client.channel != target_channel:
        await voice_client.move_to(target_channel)

    if voice_client.is_playing():
        voice_client.stop()

    def after_playing(error):
        if error:
            print(f'Error: {error}')

        async def disconnect_safely():
            await asyncio.sleep(0.5)
            if voice_client.is_connected() and not voice_client.is_playing():
                await voice_client.disconnect()

        bot.loop.create_task(disconnect_safely())

    raw_source = disnake.FFmpegPCMAudio(file_path, **FFMPEG_OPTIONS)
    source = disnake.PCMVolumeTransformer(raw_source, volume=1.0)
    voice_client.play(source, after=after_playing)

    print(f'Playing {sound_name} in channel {target_channel}')

@bot.command(aliases=["p"])
async def play(ctx: commands.Context, play_contex: str = None, game_type: str = None, mmr: int = 0, pos: int = 0):
    if play_contex is None or play_contex.lower() in ("help", "h"):
        commands_list = "\n".join(
            f"• `!play {name}` — {desc}"
            for name, desc in PLAY_SUBCOMMANDS.items()
        )
        usage_example = (
            "\n\n**Example:**\n"
            "`!play search turbo 3500 1`\n"
            "`!p s ranked 5200 2`\n"
            "`!p s lp 0 5`"
        )
        await ctx.send(f"**Available subcommands for `!play`**\n{commands_list}{usage_example}")
        return

    if play_contex and play_contex.lower() in ("1v1", "1x1"):
        mode_title = "duel(1x1)"
        voice_base = "1x1"
        embed_color = disnake.Color.dark_gold()

        voice_channel = await get_or_create_voice_channel(ctx.guild, voice_base)

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
            color=embed_color
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_field(name="🎯 Game Mode", value=f"`{mode_title}`", inline=True)
        embed.add_field(name="👥 Slots", value="`1 vs 1`", inline=True)
        embed.add_field(name="🔊 Voice Channel", value=voice_channel.mention, inline=False)
        embed.set_footer(text="Click the button below to accept the challenge!")

        join_view = JoinVoiceView(
            guild_id=ctx.guild.id,
            voice_channel_id=voice_channel.id,
            creator_id=ctx.author.id
        )

        target_channel = bot.get_channel(LFG_CHANNEL_ID)
        if target_channel:
            await target_channel.send(embed=embed, view=join_view)
            if ctx.channel.id != target_channel.id:
                await ctx.send(f"✅ Announcement posted in {target_channel.mention}!", delete_after=5)
        else:
            await ctx.send(embed=embed, view=join_view)
        return

    action = play_contex.lower()

    if action in ("search", "s"):
        if game_type is None or mmr <= 0 and game_type.lower() not in ("lp", "лп", "turbo", "турбо"):
            pass

        if game_type is None or pos not in range(1, 7):
            await ctx.send(
                "❌ **Invalid parameters!**\n"
                "Usage: `!play search <mode> <mmr> <pos (1-6)>`\n"
                "Example: `!p s ranked 4500 2`"
            )
            return

        match game_type.lower():
            case "turbo" | "турбо":
                mode_title = "Turbo"
                voice_base = "Turbo"
                embed_color = disnake.Color.orange()
            case "all_pick" | "алпик" | "аллпик" | "ap" | "unranked":
                mode_title = "All Pick (Unranked)"
                voice_base = "All Pick"
                embed_color = disnake.Color.green()
            case "ranked" | "рейт" | "рейтинг" | "rank":
                mode_title = "Ranked Matchmaking"
                voice_base = "Ranked"
                embed_color = disnake.Color.red()
            case "lp" | "лп" | "low_priority":
                mode_title = "Low Priority (Single Draft)"
                voice_base = "LP"
                embed_color = disnake.Color.dark_gray()
            case _:
                await ctx.send("❌ Unknown game mode! Choose: `turbo`, `all_pick`, `ranked`, or `lp`.")
                return

        rank_name, rank_file_name = get_rank_info(mmr)

        # Генеруємо комбіновану аватарку
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

        join_view = JoinVoiceView(
            guild_id=ctx.guild.id, 
            voice_channel_id=voice_channel.id, 
            creator_id=ctx.author.id
        )

        target_channel = bot.get_channel(LFG_CHANNEL_ID)
        send_files = [avatar_file] if avatar_file else []

        if target_channel:
            await target_channel.send(embed=embed, view=join_view, files=send_files)
            if ctx.channel.id != target_channel.id:
                await ctx.send(f"✅ Announcement posted in {target_channel.mention}!", delete_after=5)
        else:
            await ctx.send(embed=embed, view=join_view, files=send_files)
        return

@bot.event
async def on_voice_state_update(member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
    if before.channel is not None and before.channel != after.channel:
        channel = before.channel
        
        if channel.category_id == VOICE_CATEGORY_ID:
            if len(channel.members) == 0:
                await asyncio.sleep(60)
                
                try:
                    current_channel = member.guild.get_channel(channel.id)
                    if current_channel and len(current_channel.members) == 0:
                        await current_channel.delete(reason="LFG voice channel remained empty for 1 minute.")
                        print(f"Deleted empty voice channel: {channel.name}")
                except disnake.NotFound:
                    pass
                except disnake.Forbidden:
                    print(f"Missing permissions to delete channel: {channel.name}")

@bot.command(aliases=["h"])
async def help(ctx: commands.Context):
    commands_list = "\n".join(
        f"• `!{name}` — {desc}"
        for name, desc in SUBCOMMANDS.items()
    )
    
    message = (
         "**Available subcommands for `!help`**\n"
        f"{commands_list}\n"
    )
            
    await ctx.send(message)

@bot.command(aliases=["d"])
async def dota(ctx: commands.Context, dota_contex: str = None):
    if dota_contex is None:
        await ctx.send("WRITE `!dota help`")
        return

    if dota_contex and dota_contex.lower() in ("help", "h"):
            dota_commands_list = "\n".join(
                f"• `!dota {name}` — {desc}"
                for name, desc in DOTA_SUBCOMMANDS.items()
            )
            
            adm_message = (
                "**Available subcommands for `!dota`**\n"
                f"{dota_commands_list}\n"
            )
            
            await ctx.send(adm_message)
            return

    if dota_contex.lower() in ("guild", "g"):
        embed = disnake.Embed(
            title=f"⚔️ Dota 2 Guild — {DOTA_GUILD_INFO['name']}",
            description="Join our guild to complete contracts and play party ranked/unranked!",
            color=disnake.Color.red()
        )

        embed.add_field(name="🏷️ Tag", value=f"`[{DOTA_GUILD_INFO['tag']}]`", inline=True)
        embed.add_field(
            name="🆔 Leader Friend ID", 
            value=f"`{DOTA_GUILD_INFO['leader_dota_id']}`", 
            inline=True
        )

        embed.add_field(
            name="👑 Guild Leadership",
            value=(
                f"• **Leader:** [{DOTA_GUILD_INFO['leader_name']}]({DOTA_GUILD_INFO['leader_steam']})\n"
                f"• **Officer:** [{DOTA_GUILD_INFO['officer_name']}]({DOTA_GUILD_INFO['officer_steam']})"
            ),
            inline=False
        )

        embed.add_field(
            name="📌 How to join via Leader:",
            value=(
                f"1. Copy Leader's Friend ID: `{DOTA_GUILD_INFO['leader_dota_id']}`\n"
                "2. Open Dota 2 -> Friends -> **Add Friend** (or search in Guilds by name).\n"
                "3. Open the profile -> **View Guild** -> **Apply to Guild**."
            ),
            inline=False
        )

        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}", 
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

    if dota_contex and dota_contex.lower() in ("random", "r"):
        available_heroes = get_available_heroes()

        if not available_heroes:
            await ctx.send(f"Error: No hero GIF files found in `{HEROES_GIF_DIR}`.")
            return

        hero_data = random.choice(available_heroes)
        hero_name = hero_data["name"]
        hero_gif_path = hero_data["file_path"]

        position = random.choice(DOTA_POSITIONS)
        boot_id = random.randint(1, 5)
        chosen_items = random.sample(list(range(1, 64)), 5)

        try:
            inv_buffer = generate_inventory_image(boot_id, chosen_items)
        except Exception as e:
            await ctx.send(f"Error generating item layout: {e}")
            return

        hero_file = disnake.File(hero_gif_path, filename="hero.gif")
        inventory_file = disnake.File(fp=inv_buffer, filename="inventory.png")

        embed = disnake.Embed(
            title=f"🎲 Hero Roulette: {hero_name}",
            description=f"📍 **Position:** `{position}`\n🎒 **RANDOM Item Build:**",
            color=disnake.Color.gold(),
        )

        embed.set_thumbnail(url="attachment://hero.gif")

        embed.set_image(url="attachment://inventory.png")

        embed.set_footer(
            text=f"Rolled by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed, files=[hero_file, inventory_file])
        return

    if dota_contex and dota_contex.lower() in ("hero", "signa"):
        available_heroes = get_available_heroes()

        if not available_heroes:
            await ctx.send(f"Error: No hero GIF files found in `{HEROES_GIF_DIR}`.")
            return

        hero = random.choice(available_heroes)

        gif_file = disnake.File(hero["file_path"], filename=hero["file_name"])

        embed = disnake.Embed(
            title=f"🎭 Random Hero: {hero['name']}",
            description=(
                f"You rolled **{hero['name']}**!\n"
                "Check out current pro builds and meta stats using the buttons below:"
            ),
            color=disnake.Color.dark_red()
        )

        embed.set_image(url=f"attachment://{hero['file_name']}")
        embed.set_footer(
            text=f"Rolled by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        view = DotaLinksView(
            d2pt_slug=hero["d2pt_slug"],
            dotabuff_slug=hero["dotabuff_slug"]
        )
        await ctx.send(embed=embed, file=gif_file, view=view)

    if dota_contex and dota_contex.lower() in ("meta", "m", "мета", "м"):
        embed = disnake.Embed(
            title="🏆 Dota 2 Current Meta & Tier Lists",
            description=(
                "Track the strongest heroes, win rates, and trending high-MMR builds across patches:\n\n"
                "• **Dota2ProTracker Meta:** Analyzes 7k–12k+ MMR matches, pro pub builds, item timings, and hero facets.\n"
                "• **Dotabuff Meta:** Win rate and pick rate tiers categorized by skill brackets (Herald to Immortal)."
            ),
            color=disnake.Color.purple()
        )

        embed.add_field(
            name="📌 Quick ProTracker Roles:",
            value=(
                "[Carry (Pos 1)](https://dota2protracker.com/meta?mmr=7000&position=pos%2B1&period=patch&meta_period=patch) • "
                "[Mid (Pos 2)](https://dota2protracker.com/meta?mmr=7000&position=pos%2B2&period=patch&meta_period=patch) • "
                "[Offlane (Pos 3)](https://dota2protracker.com/meta?mmr=1000&position=pos%2B3&period=patch&meta_period=patch) • "
                "[Support (Pos 4/5)](https://dota2protracker.com/meta?mmr=1000&position=pos%2B5M&period=patch&meta_period=patch)"
            ),
            inline=False
        )

        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        view = DotaLinksView()
        await ctx.send(embed=embed, view=view)
        return


@bot.command(aliases=["a"])
@commands.has_permissions(administrator=True)
async def adm(ctx: commands.Context, action: str = None, amount: int = 10):
    if action is None:
        await ctx.send("WRITE !adm help")
        return

    if action and action.lower() in ("clear", "c"):
        if amount <= 0:
            await ctx.send("The number of messages must be greater than 0")

        if amount > 150:
            await ctx.send("You can delete a maximum of 150 messages at a time")

        deleted = await ctx.channel.purge(limit = amount + 1)
        confirm_msg = await ctx.send(f"Cleared **{len(deleted) - 1}** messages", delete_after=3)
        return
    
    if action and action.lower() in ("restart", "r"):
        print("Bot start restart command")
        if ctx.voice_client and ctx.voice_client.is_connected:
            await ctx.voice_client.disconnect(force=True)

        bot.is_restarting = True
        await bot.close()

    if action and action.lower() in ("close", "end", "e"):
        print("Bot close!")
        if ctx.voice_client and ctx.voice_client.is_connected:
            await ctx.voice_client.disconnect(force=True)

        bot.is_restarting = False
        await bot.close()

    if action and action.lower() in ("help", "h"):
        adm_commands_list = "\n".join(
            f"• `!adm {name}` — {desc}"
            for name, desc in ADM_SUBCOMMANDS.items()
        )
        
        adm_message = (
            "**Available subcommands for `!adm`**\n"
            f"{adm_commands_list}\n"
        )
        
        await ctx.send(adm_message)
        return
        

@adm.error
async def adm_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("SACK YOU HAVE PERMISSIONS IDIOT")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("The number of messages must be an integer! Example: `!adm clear 25`")
    else:
        print(f"Error in adm: {error}")

if __name__ == "__main__":
    TOKEN_FILE = "FILE_WITH_TOKEN"

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            bot_token = f.read().strip()
    else:
        print(f"Error: Token file '{TOKEN_FILE}' not found!")
        sys.exit()

    try:
        bot.run(bot_token)
    finally:
        if getattr(bot, "is_restarting", False):
            print("Spawning process...")
            subprocess.run([sys.executable, *sys.argv])