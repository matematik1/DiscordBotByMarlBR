import os

SOUND_DIR = "soundboard"
HEROES_GIF_DIR = os.path.join("video", "heroes")
ITEMS_B_DIR = os.path.join("img", "items", "b")
ITEMS_I_DIR = os.path.join("img", "items", "i")
RANG_DIR = os.path.join("img", "rang")

LFG_CHANNEL_ID = 1552413792795889745
VOICE_CATEGORY_ID = 1552388769649393774
AFK_VOICE_ID = 1552406299130728559
AUTO_ROLE_ID = 1543689985981546587
STEAM_API_KEY = "YOUR_STEAM_API_KEY"
STRATZ_API_KEY = "YOUR_STATZ_ZPI_KEY"

BASE_XP = 100
XP_INTERCASE = 100

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

ADM_SUBCOMMANDS = {
    "clear <n>": "Delete n messages from channel (max 150)",
    "restart": "Restart the bot instance",
    "close": "Shut down the bot completely",
    "exp <amount> [user]": "Give or remove XP (supports @mention, username, or ID)",
    "exp_update": "Recalculate all user levels and fix float XP (alias: e_u)",
    "help": "Display administrator commands reference"
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

SUBCOMMANDS = {
    "sound (s)": "Plays sounds in your voice channel",
    "dota (d)": "Dota-related commands",
    "play (p)": "Finding teammates and duels",
    "help (h)": "Displays this menu"
}

PLAY_SUBCOMMANDS = {
    "search": "Create a team search announcement \n(`!p s <mode> <mmr> <pos>`)",
    "1x1 / 1v1": "Creates a voice channel for the duel",
    "help": "Displays this menu"
}

DOTA_SUBCOMMANDS = {
    "connect <SteamID32>": "Link your Steam ID to your Discord profile",
    "profile [SteamID32]": "Show rank, winrate, and recent matches",
    "inv [SteamID32]": "Render custom Dota 2 inventory item build",
    "roll [min-max]": "Roll a dice with animation (e.g. !d roll 100-200, default: 1-100)"
}

SOUND_SUBCOMMANDS = {
    "stop": "Stopped sound",
    "list": "Displays the names of all sounds.",
    "help": "Displays this menu"
}

CENSORED_WORDS = [
    "натурал",
    "natural",
    "67",
    "нітуріл",
    "скитер",
    "скітер",
    "skiter",
    "sketer",
    "skeeter"
]

DOTA_RANK_ID = {
    0: 1553011169218793562,
    1: 1543692031308865656,
    2: 1543692447559721030,
    3: 1543692647888326656,
    4: 1543692782126764072,
    5: 1553013451100786758,
    6: 1553011430377398382,
    7: 1553012012231950366,
    8: 1553012142087868547
}