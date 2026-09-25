import os
import random
import asyncio
import disnake
from utils.config import SOUND_DIR, FFMPEG_OPTIONS

def get_sound_files() -> list[str]:
    if not os.path.exists(SOUND_DIR):
        return []
    return [f for f in os.listdir(SOUND_DIR) if f.lower().endswith((".mp3", ".wav", ".ogg"))]


class SoundSelectMenu(disnake.ui.Select):
    def __init__(self, files: list[str]):
        options = []
        for file in files[:25]:
            display_name = os.path.splitext(file)[0].replace("_", " ").title()
            options.append(
                disnake.SelectOption(
                    label=display_name[:100],
                    value=file,
                    description=f"Play {display_name}"[:100],
                    emoji="🎵"
                )
            )
        super().__init__(
            placeholder="Select a sound to play...",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )

    async def callback(self, inter: disnake.MessageInteraction):
        await self.view.play_sound(inter, self.values[0])


class UserSoundMixerView(disnake.ui.View):
    """Саундпад для обычных пользователей."""
    def __init__(self, user_id: int, bot, user_name: str, user_avatar_url: str):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.bot = bot
        self.user_name = user_name
        self.user_avatar_url = user_avatar_url
        self.volume = getattr(self.bot, "default_sound_volume", 0.4)

        self.last_sound = "None"
        self.status = "Idle"

        files = get_sound_files()
        if files:
            self.add_item(SoundSelectMenu(files))

    async def interaction_check(self, inter: disnake.MessageInteraction) -> bool:
        if inter.author.id != self.user_id:
            await inter.response.send_message("❌ This sound menu was opened by someone else!", ephemeral=True)
            return False
        return True

    def build_embed(self) -> disnake.Embed:
        embed = disnake.Embed(
            title="🔊 Soundboard",
            description=(
                f"• **Status:** `{self.status}`\n"
                f"• **Now Playing:** `{self.last_sound}`\n"
                f"• **Volume:** `{int(self.volume * 100)}%`\n\n"
                "• **Menu:** Select a sound from the dropdown\n"
                "• 🎲 **Random:** Play a random sound clip\n"
                "• ⏹️ **Stop:** Stop playback and leave voice"
            ),
            color=disnake.Color.teal()
        )
        embed.set_footer(text=f"User: {self.user_name}", icon_url=self.user_avatar_url)
        return embed

    async def play_sound(self, inter: disnake.MessageInteraction, file_name: str):
        if not inter.author.voice or not inter.author.voice.channel:
            await inter.response.send_message("⚠️ You must be connected to a voice channel!", ephemeral=True)
            return

        file_path = os.path.join(SOUND_DIR, file_name)
        if not os.path.exists(file_path):
            await inter.response.send_message("❌ Sound file not found on the server!", ephemeral=True)
            return

        target_channel = inter.author.voice.channel
        voice_client: disnake.VoiceClient = inter.guild.voice_client

        if voice_client is None:
            voice_client = await target_channel.connect(timeout=10.0, reconnect=True)
        elif voice_client.channel != target_channel:
            await voice_client.move_to(target_channel)

        for _ in range(20):
            if voice_client.is_connected():
                break
            await asyncio.sleep(0.1)

        if not voice_client.is_connected():
            await inter.response.send_message("❌ Voice connection failed. Please try again!", ephemeral=True)
            return

        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()

        def after_playing(error):
            if error:
                print(f"Playback Error: {error}")
            async def disconnect_safely():
                await asyncio.sleep(0.5)
                if voice_client.is_connected() and not voice_client.is_playing():
                    await voice_client.disconnect()
            self.bot.loop.create_task(disconnect_safely())

        raw_source = disnake.FFmpegPCMAudio(file_path, **FFMPEG_OPTIONS)
        source = disnake.PCMVolumeTransformer(raw_source, volume=self.volume)
        voice_client.play(source, after=after_playing)

        self.last_sound = os.path.splitext(file_name)[0].replace("_", " ").title()
        self.status = "Playing"
        if inter.response.is_done():
            await inter.edit_original_response(embed=self.build_embed(), view=self)
        else:
            await inter.response.edit_message(embed=self.build_embed(), view=self)

    @disnake.ui.button(label="Random", emoji="🎲", style=disnake.ButtonStyle.primary, row=1)
    async def random_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        files = get_sound_files()
        if not files:
            await inter.response.send_message("❌ No sound files available!", ephemeral=True)
            return
        await self.play_sound(inter, random.choice(files))

    @disnake.ui.button(label="Stop", emoji="⏹️", style=disnake.ButtonStyle.danger, row=1)
    async def stop_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        voice_client: disnake.VoiceClient = inter.guild.voice_client
        if voice_client and voice_client.is_connected():
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            self.status = "Stopped"
        else:
            self.status = "Disconnected"
        await inter.response.edit_message(embed=self.build_embed(), view=self)


class SoundMixerView(disnake.ui.View):
    """Полнофункциональный микшер администратора с повтором и сохранением громкости."""
    def __init__(self, admin_id: int, bot, admin_name: str, admin_avatar_url: str):
        super().__init__(timeout=180)
        self.admin_id = admin_id
        self.bot = bot
        self.admin_name = admin_name
        self.admin_avatar_url = admin_avatar_url

        if not hasattr(self.bot, "default_sound_volume"):
            self.bot.default_sound_volume = 0.4
        self.volume = self.bot.default_sound_volume

        self.last_sound = "None"
        self.current_file = None
        self.is_looping = False
        self.status = "Idle"
        self.notice = f"Default volume: {int(self.bot.default_sound_volume * 100)}%"

        files = get_sound_files()
        if files:
            self.add_item(SoundSelectMenu(files))

    def build_embed(self) -> disnake.Embed:
        loop_status = "🔁 ON" if self.is_looping else "OFF"
        embed = disnake.Embed(
            title="🎛️ Sound Mixer & Audio Control",
            description=(
                f"• **Status:** `{self.status}`\n"
                f"• **Now Playing:** `{self.last_sound}`\n"
                f"• **Loop:** `{loop_status}`\n"
                f"• **Current Volume:** `{int(self.volume * 100)}%`\n"
                f"• **Saved Default:** `{int(self.bot.default_sound_volume * 100)}%`\n"
                f"• **Note:** *{self.notice}*\n\n"
                "───────────────────────────\n"
                "• **Menu:** Select a track from the list\n"
                "• 🎲 **Random** | 🔁 **Repeat** | ⏹️ **Stop**\n"
                "• 🔉 / 🔊 / 🔄 **Volume** | 💾 **Save Vol**"
            ),
            color=disnake.Color.dark_theme()
        )
        embed.set_footer(text=f"Admin: {self.admin_name}", icon_url=self.admin_avatar_url)
        return embed

    async def interaction_check(self, inter: disnake.MessageInteraction) -> bool:
        if inter.author.id != self.admin_id and not inter.author.guild_permissions.administrator:
            await inter.response.send_message("❌ Admin-only mixer interaction!", ephemeral=True)
            return False
        return True

    def _start_playback(self, voice_client: disnake.VoiceClient, file_path: str):
        def after_playing(error):
            if error:
                print(f"Playback Error: {error}")
            if self.is_looping and voice_client.is_connected() and self.current_file:
                current_path = os.path.join(SOUND_DIR, self.current_file)
                if os.path.exists(current_path):
                    self._start_playback(voice_client, current_path)
                    return
            async def disconnect_safely():
                await asyncio.sleep(0.5)
                if voice_client.is_connected() and not voice_client.is_playing() and not self.is_looping:
                    await voice_client.disconnect()
            self.bot.loop.create_task(disconnect_safely())

        raw_source = disnake.FFmpegPCMAudio(file_path, **FFMPEG_OPTIONS)
        source = disnake.PCMVolumeTransformer(raw_source, volume=self.volume)
        voice_client.play(source, after=after_playing)

    async def play_sound(self, inter: disnake.MessageInteraction, file_name: str):
        if not inter.author.voice or not inter.author.voice.channel:
            await inter.response.send_message("⚠️ You must be connected to a voice channel!", ephemeral=True)
            return

        file_path = os.path.join(SOUND_DIR, file_name)
        if not os.path.exists(file_path):
            await inter.response.send_message("❌ Sound file not found on the server!", ephemeral=True)
            return

        target_channel = inter.author.voice.channel
        voice_client: disnake.VoiceClient = inter.guild.voice_client

        if voice_client is None:
            voice_client = await target_channel.connect(timeout=10.0, reconnect=True)
        elif voice_client.channel != target_channel:
            await voice_client.move_to(target_channel)

        for _ in range(20):
            if voice_client.is_connected():
                break
            await asyncio.sleep(0.1)

        if not voice_client.is_connected():
            await inter.response.send_message("❌ Voice connection failed. Please try again!", ephemeral=True)
            return

        if voice_client.is_playing():
            voice_client.stop()

        self.current_file = file_name
        self._start_playback(voice_client, file_path)

        self.last_sound = os.path.splitext(file_name)[0].replace("_", " ").title()
        self.status = "Playing" if not self.is_looping else "Playing (Loop)"
        self.notice = "Playing requested track"
        if inter.response.is_done():
            await inter.edit_original_response(embed=self.build_embed(), view=self)
        else:
            await inter.response.edit_message(embed=self.build_embed(), view=self)

    @disnake.ui.button(label="Random", emoji="🎲", style=disnake.ButtonStyle.primary, row=1)
    async def random_track(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        files = get_sound_files()
        if not files:
            await inter.response.send_message("❌ No sound files available!", ephemeral=True)
            return
        await self.play_sound(inter, random.choice(files))

    @disnake.ui.button(label="Repeat", emoji="🔁", style=disnake.ButtonStyle.secondary, row=1)
    async def repeat_track(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if not self.current_file:
            await inter.response.send_message("⚠️ Play a track first before enabling repeat!", ephemeral=True)
            return
        self.is_looping = not self.is_looping
        button.style = disnake.ButtonStyle.success if self.is_looping else disnake.ButtonStyle.secondary
        self.notice = "Loop enabled" if self.is_looping else "Loop disabled"
        await inter.response.edit_message(embed=self.build_embed(), view=self)

    @disnake.ui.button(label="Stop", emoji="⏹️", style=disnake.ButtonStyle.danger, row=1)
    async def stop_track(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.is_looping = False
        self.current_file = None
        for child in self.children:
            if isinstance(child, disnake.ui.Button) and child.label == "Repeat":
                child.style = disnake.ButtonStyle.secondary

        voice_client: disnake.VoiceClient = inter.guild.voice_client
        if voice_client and voice_client.is_connected():
            if voice_client.is_playing():
                voice_client.stop()
            await voice_client.disconnect()
            self.status = "Stopped"
        else:
            self.status = "Disconnected"
        self.notice = "Playback stopped"
        await inter.response.edit_message(embed=self.build_embed(), view=self)

    @disnake.ui.button(label="-20%", emoji="🔉", style=disnake.ButtonStyle.secondary, row=2)
    async def lower_volume(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.volume = max(0.1, round(self.volume - 0.2, 2))
        voice_client: disnake.VoiceClient = inter.guild.voice_client
        if voice_client and voice_client.source and hasattr(voice_client.source, "volume"):
            voice_client.source.volume = self.volume
        self.notice = f"Volume lowered to {int(self.volume * 100)}%"
        await inter.response.edit_message(embed=self.build_embed(), view=self)

    @disnake.ui.button(label="+20%", emoji="🔊", style=disnake.ButtonStyle.secondary, row=2)
    async def raise_volume(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.volume = min(2.0, round(self.volume + 0.2, 2))
        voice_client: disnake.VoiceClient = inter.guild.voice_client
        if voice_client and voice_client.source and hasattr(voice_client.source, "volume"):
            voice_client.source.volume = self.volume
        self.notice = f"Volume raised to {int(self.volume * 100)}%"
        await inter.response.edit_message(embed=self.build_embed(), view=self)

    @disnake.ui.button(label="100%", emoji="🔄", style=disnake.ButtonStyle.secondary, row=2)
    async def reset_volume(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.volume = 1.0
        voice_client: disnake.VoiceClient = inter.guild.voice_client
        if voice_client and voice_client.source and hasattr(voice_client.source, "volume"):
            voice_client.source.volume = 1.0
        self.notice = "Volume reset to default 100%"
        await inter.response.edit_message(embed=self.build_embed(), view=self)

    @disnake.ui.button(label="Save Vol", emoji="💾", style=disnake.ButtonStyle.success, row=2)
    async def save_volume(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.bot.default_sound_volume = self.volume
        self.notice = f"Volume {int(self.volume * 100)}% saved as default!"
        await inter.response.edit_message(embed=self.build_embed(), view=self)