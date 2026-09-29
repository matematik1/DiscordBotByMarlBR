import asyncio
import json
import os
import random
from pathlib import Path
from typing import Optional

import disnake

from utils.config import SOUND_DIR, FFMPEG_OPTIONS

AUDIO_EXTENSIONS = (".mp3", ".wav", ".ogg", ".flac", ".m4a")
PAGE_SIZE = 25
MAX_VOLUME = 1.0
VOLUME_STEP = 0.10
SOUND_SETTINGS_FILE = os.path.join("data", "sound_settings.json")

# Playback state is shared by !sound and /sound.
# This is what makes Repeat work even when it is toggled after playback started.
_PLAYBACKS: dict[int, dict] = {}


def _normal_path(path: str) -> str:
    return path.replace("\\", "/")


def get_sound_files() -> list[str]:
    root = Path(SOUND_DIR)
    if not root.exists():
        return []
    return sorted(
        _normal_path(path.relative_to(root).as_posix())
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    )


def get_sound_categories(files: Optional[list[str]] = None) -> list[str]:
    files = get_sound_files() if files is None else files
    categories = {"General"}
    for file_name in files:
        parts = _normal_path(file_name).split("/")
        if len(parts) > 1:
            categories.add(parts[0])
    return sorted(categories, key=str.casefold)


def get_category_files(category: str, files: Optional[list[str]] = None) -> list[str]:
    files = get_sound_files() if files is None else files
    if category == "General":
        return sorted(
            [f for f in files if "/" not in _normal_path(f)],
            key=str.casefold,
        )
    prefix = category.rstrip("/") + "/"
    return sorted(
        [f for f in files if _normal_path(f).startswith(prefix)],
        key=str.casefold,
    )


def sound_display_name(file_name: str) -> str:
    return Path(file_name).stem.replace("_", " ").replace("-", " ").strip().title()


def sound_label(file_name: str) -> str:
    parts = _normal_path(file_name).split("/")
    if len(parts) == 1:
        return sound_display_name(file_name)
    return f"{parts[-2]} / {sound_display_name(file_name)}"


def find_sound(query: str, files: Optional[list[str]] = None) -> Optional[str]:
    files = get_sound_files() if files is None else files
    q = _normal_path(query).strip().casefold()
    if not q:
        return None

    exact_path = [
        f for f in files
        if q in (_normal_path(f).casefold(), Path(f).stem.casefold())
    ]
    if exact_path:
        return exact_path[0]

    exact_display = [
        f for f in files
        if q == sound_display_name(f).casefold()
    ]
    if exact_display:
        return exact_display[0]

    matches = [
        f for f in files
        if q in _normal_path(f).casefold()
        or q in Path(f).stem.casefold()
    ]
    return matches[0] if matches else None


def find_sound_matches(query: str, limit: int = 25) -> list[str]:
    files = get_sound_files()
    q = query.casefold().strip()

    if not q:
        return files[:limit]

    exact, starts, contains = [], [], []
    for file_name in files:
        path_l = _normal_path(file_name).casefold()
        stem_l = Path(file_name).stem.casefold()

        if q == path_l or q == stem_l:
            exact.append(file_name)
        elif path_l.startswith(q) or stem_l.startswith(q):
            starts.append(file_name)
        elif q in path_l or q in stem_l:
            contains.append(file_name)

    return (exact + starts + contains)[:limit]


def _load_sound_settings() -> dict:
    path = Path(SOUND_SETTINGS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        return {"default_volume": 0.5}

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {"default_volume": 0.5}
    except (OSError, json.JSONDecodeError):
        return {"default_volume": 0.5}


def get_default_volume(bot=None) -> float:
    # Always read the saved value. This prevents main.py's old
    # bot.default_sound_volume = 0.5 from overwriting the saved default.
    try:
        value = float(_load_sound_settings().get("default_volume", 0.5))
    except (TypeError, ValueError):
        value = 0.5

    value = max(0.0, min(MAX_VOLUME, value))

    if bot is not None:
        bot.default_sound_volume = value

    return value


def save_default_volume(bot, volume: float) -> None:
    volume = max(0.0, min(MAX_VOLUME, float(volume)))

    path = Path(SOUND_SETTINGS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump({"default_volume": volume}, file, indent=2)

    bot.default_sound_volume = volume


def get_playback_state(guild_id: int) -> dict:
    return _PLAYBACKS.setdefault(
        guild_id,
        {
            "file": None,
            "repeat": False,
            "volume": 0.5,
            "generation": 0,
        },
    )


def set_repeat(guild_id: int, enabled: bool) -> None:
    get_playback_state(guild_id)["repeat"] = bool(enabled)


def get_repeat(guild_id: int) -> bool:
    return bool(get_playback_state(guild_id)["repeat"])


def invalidate_playback(guild_id: int) -> None:
    state = get_playback_state(guild_id)
    state["generation"] += 1
    state["file"] = None


async def ensure_voice_client(inter, bot):
    if not inter.guild:
        return None, "❌ This command can only be used inside a server."

    if not inter.author.voice or not inter.author.voice.channel:
        return None, "⚠️ You must be connected to a voice channel first."

    target_channel = inter.author.voice.channel
    voice_client = inter.guild.voice_client

    try:
        if voice_client is None or not voice_client.is_connected():
            voice_client = await target_channel.connect(timeout=10.0, reconnect=True)
        elif voice_client.channel != target_channel:
            await voice_client.move_to(target_channel)
    except Exception as exc:
        print(f"[Sound] Voice connection error: {exc!r}")
        return None, "❌ I couldn't connect to your voice channel."

    return voice_client, None


def _make_source(file_name: str, volume: float):
    file_path = os.path.join(SOUND_DIR, *file_name.split("/"))
    return disnake.PCMVolumeTransformer(
        disnake.FFmpegPCMAudio(file_path, **FFMPEG_OPTIONS),
        volume=max(0.0, min(MAX_VOLUME, volume)),
    )


def start_playback(
    bot,
    guild_id: int,
    voice_client: disnake.VoiceClient,
    file_name: str,
    volume: float,
) -> None:
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

    state = get_playback_state(guild_id)
    state["generation"] += 1
    generation = state["generation"]
    state["file"] = file_name
    state["volume"] = max(0.0, min(MAX_VOLUME, volume))

    def play_current():
        if not voice_client.is_connected():
            return

        current = get_playback_state(guild_id)
        if current["generation"] != generation or current["file"] != file_name:
            return

        file_path = os.path.join(SOUND_DIR, *file_name.split("/"))
        if not os.path.isfile(file_path):
            return

        source = _make_source(file_name, current["volume"])

        def after_playing(error):
            if error:
                print(f"[Sound] Playback error for {file_name}: {error}")

            async def finished():
                await asyncio.sleep(0.2)

                current = get_playback_state(guild_id)
                if current["generation"] != generation:
                    return

                if (
                    current["repeat"]
                    and current["file"] == file_name
                    and voice_client.is_connected()
                ):
                    play_current()
                    return

                if voice_client.is_connected() and not voice_client.is_playing():
                    try:
                        await voice_client.disconnect()
                    except Exception:
                        pass

            bot.loop.call_soon_threadsafe(
                lambda: bot.loop.create_task(finished())
            )

        voice_client.play(source, after=after_playing)

    play_current()


def set_current_volume(guild_id: int, volume: float) -> float:
    volume = max(0.0, min(MAX_VOLUME, float(volume)))
    state = get_playback_state(guild_id)
    state["volume"] = volume
    return volume


def apply_current_volume(guild_id: int, guild, volume: float) -> None:
    volume = set_current_volume(guild_id, volume)
    voice_client = guild.voice_client if guild else None

    if voice_client and voice_client.source:
        source = voice_client.source
        if isinstance(source, disnake.PCMVolumeTransformer):
            source.volume = volume


async def play_sound_direct(inter, bot, file_name: str, volume: Optional[float] = None):
    safe_file = _normal_path(file_name)
    root = os.path.abspath(SOUND_DIR)
    target = os.path.abspath(os.path.join(SOUND_DIR, *safe_file.split("/")))

    if not target.startswith(root + os.sep) or not os.path.isfile(target):
        return False, "❌ Sound file not found."

    voice_client, error = await ensure_voice_client(inter, bot)
    if error:
        return False, error

    if volume is None:
        volume = get_default_volume(bot)

    start_playback(
        bot,
        inter.guild.id,
        voice_client,
        safe_file,
        volume,
    )
    return True, sound_display_name(safe_file)


class CategorySelect(disnake.ui.Select):
    def __init__(self, view):
        self.sound_view = view
        categories = view.categories[:25]

        options = [
            disnake.SelectOption(
                label=("📁 " + category)[:100],
                value=category,
                default=category == view.category,
            )
            for category in categories
        ]

        super().__init__(
            placeholder="📁 Select a category...",
            options=options or [
                disnake.SelectOption(label="No categories", value="__empty__")
            ],
            row=0,
        )

    async def callback(self, inter):
        value = self.values[0]
        if value == "__empty__":
            await inter.response.send_message("❌ No categories found.", ephemeral=True)
            return

        self.sound_view.category = value
        self.sound_view.page = 0
        self.sound_view.rebuild()
        await inter.response.edit_message(
            embed=self.sound_view.build_embed(),
            view=self.sound_view,
        )


class TrackSelect(disnake.ui.Select):
    def __init__(self, view):
        self.sound_view = view
        files = view.page_files

        options = [
            disnake.SelectOption(
                label=sound_label(file_name)[:100],
                value=file_name,
                description=f"Play {sound_display_name(file_name)}"[:100],
                emoji="🎵",
            )
            for file_name in files
        ]

        super().__init__(
            placeholder="🎵 Select a sound...",
            options=options or [
                disnake.SelectOption(
                    label="No sounds in this category",
                    value="__empty__",
                )
            ],
            row=1,
        )

    async def callback(self, inter):
        value = self.values[0]
        if value == "__empty__":
            await inter.response.send_message(
                "❌ This category has no sounds.",
                ephemeral=True,
            )
            return

        await self.sound_view.play_sound(inter, value)


class BaseSoundView(disnake.ui.View):
    def __init__(
        self,
        guild_id: int,
        user_id: int,
        bot,
        user_name: str,
        user_avatar_url: str,
        admin: bool = False,
    ):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.user_id = user_id
        self.bot = bot
        self.user_name = user_name
        self.user_avatar_url = user_avatar_url
        self.admin = admin

        state = get_playback_state(guild_id)
        self.volume = state["volume"] if state["file"] else get_default_volume(bot)
        self.last_sound = sound_display_name(state["file"]) if state["file"] else "None"
        self.status = "Playing" if state["file"] else "Idle"
        self.notice = "Ready"
        self.category = "General"
        self.page = 0
        self.rebuild()

    @property
    def files(self):
        return get_sound_files()

    @property
    def categories(self):
        return get_sound_categories(self.files)

    @property
    def category_files(self):
        return get_category_files(self.category, self.files)

    @property
    def page_files(self):
        start = self.page * PAGE_SIZE
        return self.category_files[start:start + PAGE_SIZE]

    @property
    def page_count(self):
        return max(1, (len(self.category_files) + PAGE_SIZE - 1) // PAGE_SIZE)

    @property
    def repeat_enabled(self):
        return get_repeat(self.guild_id)

    def build_embed(self):
        embed = disnake.Embed(
            title="🔊 Sound Mixer",
            description=(
                f"• **Status:** `{self.status}`\n"
                f"• **Now Playing:** `{self.last_sound}`\n"
                f"• **Category:** `{self.category}`\n"
                f"• **Page:** `{self.page + 1}/{self.page_count}`\n"
                f"• **Repeat:** `{'ON' if self.repeat_enabled else 'OFF'}`\n"
                f"• **Volume:** `{int(self.volume * 100)}%`\n\n"
                "Select a category, then a sound. "
                "Use ⬅️/➡️ for pages."
            ),
            color=disnake.Color.teal(),
        )

        if self.admin:
            embed.description += "\n🔐 You can save the default volume."
        else:
            embed.description += "\n👤 Your volume changes are temporary."

        return embed

    def rebuild(self):
        self.clear_items()
        self.add_item(CategorySelect(self))
        self.add_item(TrackSelect(self))

        previous = disnake.ui.Button(
            label="Previous",
            emoji="⬅️",
            style=disnake.ButtonStyle.secondary,
            disabled=self.page <= 0,
            row=2,
        )
        next_button = disnake.ui.Button(
            label="Next",
            emoji="➡️",
            style=disnake.ButtonStyle.secondary,
            disabled=self.page >= self.page_count - 1,
            row=2,
        )

        async def previous_callback(inter):
            self.page = max(0, self.page - 1)
            self.rebuild()
            await inter.response.edit_message(embed=self.build_embed(), view=self)

        async def next_callback(inter):
            self.page = min(self.page_count - 1, self.page + 1)
            self.rebuild()
            await inter.response.edit_message(embed=self.build_embed(), view=self)

        previous.callback = previous_callback
        next_button.callback = next_callback
        self.add_item(previous)
        self.add_item(next_button)

        random_button = disnake.ui.Button(
            label="Random",
            emoji="🎲",
            style=disnake.ButtonStyle.primary,
            row=3,
        )
        repeat_button = disnake.ui.Button(
            label=f"Repeat: {'ON' if self.repeat_enabled else 'OFF'}",
            emoji="🔁",
            style=(
                disnake.ButtonStyle.success
                if self.repeat_enabled
                else disnake.ButtonStyle.secondary
            ),
            row=3,
        )
        stop_button = disnake.ui.Button(
            label="Stop",
            emoji="⏹️",
            style=disnake.ButtonStyle.danger,
            row=3,
        )

        async def random_callback(inter):
            files = self.category_files
            if not files:
                await inter.response.send_message(
                    "❌ No sounds in this category.",
                    ephemeral=True,
                )
                return

            await self.play_sound(inter, random.choice(files))

        async def repeat_callback(inter):
            enabled = not get_repeat(self.guild_id)
            set_repeat(self.guild_id, enabled)
            self.notice = "Repeat enabled" if enabled else "Repeat disabled"
            self.rebuild()
            await inter.response.edit_message(
                embed=self.build_embed(),
                view=self,
            )

        async def stop_callback(inter):
            invalidate_playback(self.guild_id)
            voice_client = inter.guild.voice_client

            if voice_client and voice_client.is_connected():
                if voice_client.is_playing() or voice_client.is_paused():
                    voice_client.stop()
                try:
                    await voice_client.disconnect()
                except Exception:
                    pass

            self.status = "Stopped"
            self.last_sound = "None"
            self.notice = "Playback stopped"
            set_repeat(self.guild_id, False)
            self.rebuild()
            await inter.response.edit_message(
                embed=self.build_embed(),
                view=self,
            )

        random_button.callback = random_callback
        repeat_button.callback = repeat_callback
        stop_button.callback = stop_callback

        self.add_item(random_button)
        self.add_item(repeat_button)
        self.add_item(stop_button)

        down = disnake.ui.Button(label="-10%", emoji="🔉", row=4)
        up = disnake.ui.Button(label="+10%", emoji="🔊", row=4)
        reset = disnake.ui.Button(label="Reset", emoji="🔄", row=4)

        async def down_callback(inter):
            self.volume = max(0.0, round(self.volume - VOLUME_STEP, 2))
            apply_current_volume(self.guild_id, inter.guild, self.volume)
            self.notice = f"Volume: {int(self.volume * 100)}%"
            self.rebuild()
            await inter.response.edit_message(embed=self.build_embed(), view=self)

        async def up_callback(inter):
            self.volume = min(MAX_VOLUME, round(self.volume + VOLUME_STEP, 2))
            apply_current_volume(self.guild_id, inter.guild, self.volume)
            self.notice = f"Volume: {int(self.volume * 100)}%"
            self.rebuild()
            await inter.response.edit_message(embed=self.build_embed(), view=self)

        async def reset_callback(inter):
            self.volume = get_default_volume(self.bot)
            apply_current_volume(self.guild_id, inter.guild, self.volume)
            self.notice = f"Reset to default: {int(self.volume * 100)}%"
            self.rebuild()
            await inter.response.edit_message(embed=self.build_embed(), view=self)

        down.callback = down_callback
        up.callback = up_callback
        reset.callback = reset_callback

        self.add_item(down)
        self.add_item(up)
        self.add_item(reset)

        # Only admin panel gets a persistent Save button.
        if self.admin:
            save = disnake.ui.Button(
                label="Save default",
                emoji="💾",
                style=disnake.ButtonStyle.success,
                row=4,
            )

            async def save_callback(inter):
                if not inter.author.guild_permissions.manage_guild:
                    await inter.response.send_message(
                        "❌ You need Manage Server to save the default volume.",
                        ephemeral=True,
                    )
                    return

                save_default_volume(self.bot, self.volume)
                self.notice = f"Default saved: {int(self.volume * 100)}%"
                await inter.response.edit_message(
                    embed=self.build_embed(),
                    view=self,
                )

            save.callback = save_callback
            self.add_item(save)

    async def interaction_check(self, inter) -> bool:
        if inter.author.id != self.user_id:
            await inter.response.send_message(
                "❌ This sound mixer belongs to another user.",
                ephemeral=True,
            )
            return False
        return True

    async def play_sound(self, inter, file_name: str):
        safe_file = _normal_path(file_name)

        if safe_file not in self.files:
            await inter.response.send_message(
                "❌ Sound file no longer exists.",
                ephemeral=True,
            )
            return

        voice_client, error = await ensure_voice_client(inter, self.bot)
        if error:
            await inter.response.send_message(error, ephemeral=True)
            return

        self.volume = max(0.0, min(MAX_VOLUME, self.volume))
        start_playback(
            self.bot,
            self.guild_id,
            voice_client,
            safe_file,
            self.volume,
        )

        self.last_sound = sound_display_name(safe_file)
        self.status = "Playing"
        self.notice = "Playing track"

        await inter.response.edit_message(
            embed=self.build_embed(),
            view=self,
        )


class UserSoundMixerView(BaseSoundView):
    def __init__(self, guild_id, user_id, bot, user_name, user_avatar_url):
        super().__init__(
            guild_id,
            user_id,
            bot,
            user_name,
            user_avatar_url,
            admin=False,
        )


class SoundMixerView(BaseSoundView):
    def __init__(self, guild_id, user_id, bot, user_name, user_avatar_url):
        super().__init__(
            guild_id,
            user_id,
            bot,
            user_name,
            user_avatar_url,
            admin=True,
        )


async def open_user_mixer(ctx_or_inter, bot, ephemeral=False):
    if not get_sound_files():
        await ctx_or_inter.send(
            "⚠️ No audio files found in the sound directory.",
            ephemeral=True,
        ) if hasattr(ctx_or_inter, "response") else await ctx_or_inter.send(
            "⚠️ No audio files found in the sound directory."
        )
        return

    is_interaction = hasattr(ctx_or_inter, "response")

    view = UserSoundMixerView(
        ctx_or_inter.guild.id,
        ctx_or_inter.author.id,
        bot,
        ctx_or_inter.author.display_name,
        ctx_or_inter.author.display_avatar.url,
    )

    if is_interaction:
        await ctx_or_inter.response.send_message(
            embed=view.build_embed(),
            view=view,
            ephemeral=ephemeral,
        )
    else:
        await ctx_or_inter.send(embed=view.build_embed(), view=view)


async def open_admin_mixer(ctx_or_inter, bot, ephemeral=True):
    is_interaction = hasattr(ctx_or_inter, "response")

    view = SoundMixerView(
        ctx_or_inter.guild.id,
        ctx_or_inter.author.id,
        bot,
        ctx_or_inter.author.display_name,
        ctx_or_inter.author.display_avatar.url,
    )

    if is_interaction:
        await ctx_or_inter.response.send_message(
            embed=view.build_embed(),
            view=view,
            ephemeral=ephemeral,
        )
    else:
        await ctx_or_inter.send(embed=view.build_embed(), view=view)
