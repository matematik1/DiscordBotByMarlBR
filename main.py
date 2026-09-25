import os
import sys
import subprocess
import disnake
from disnake.ext import commands
from utils.config import SUBCOMMANDS, AUTO_ROLE_ID

intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!", 
    intents=disnake.Intents.all(), 
    help_command=None,
    case_insensitive=True,
    test_guilds=[1543687732105052348]
)

bot.default_sound_volume = 0.5
bot.is_restarting = False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.event
async def on_member_join(member: disnake.Member):
    role = member.guild.get_role(AUTO_ROLE_ID)
    if role is not None:
        await member.add_roles(role)
        print(f'Given role {role.name} to {member.name}')

@bot.command(name="help", aliases=["h"])
async def help_command(ctx: commands.Context):
    embed = disnake.Embed(
        title="📖 Bot Command Center",
        description="Here is the list of all available bot modules and commands:",
        color=disnake.Color.blurple()
    )

    # 1. DOTA 2
    embed.add_field(
        name="🎮 Dota 2 (`!dota` / `!d`)",
        value=(
            "• `!d help` — Open detailed Dota 2 command menu (alias: `!d h`)\n"
            "• `!d connect <SteamID>` — Link your Steam account\n"
            "• `!d profile [SteamID]` — Display rank, win rate, and recent games\n"
            "• `!d inv [SteamID]` — Render active hero inventory build\n"
            "• `!d roll [min-max]` — Roll dice with animation (e.g., `!d roll 100-200`)"
        ),
        inline=False
    )

    # 2. EXPERIENCE & LEVELS
    embed.add_field(
        name="✨ Experience & Levels",
        value=(
            "• `!exp_help` — Open leveling guide and XP details (alias: `!eh`)\n"
            "• `!rank [user]` — View your level and XP progress (aliases: `!lvl`, `!level`)\n"
            "• `!top` — Show server experience leaderboard (aliases: `!t`, `!lider`)"
        ),
        inline=False
    )

    # 3. PARTY FINDER (PLAY)
    embed.add_field(
        name="👥 Party Finder (`!play` / `!p`)",
        value=(
            "• `!play help` — View party lobby controls and instructions\n"
            "• `!play` — Open interactive party search lobby with reaction buttons"
        ),
        inline=False
    )

    embed.add_field(
        name="⚔️ Duels (`!duel`)",
        value=(
            "• `!duel @user` — Classic 50/50 western shootout\n"
            "• `!duel rr @user` — Step-by-step 6-round Russian Roulette"
        ),
        inline=False
    )

    # 4. SOUNDPAD / AUDIO
    embed.add_field(
        name="🔊 Soundpad (`!sound` / `!s`)",
        value=(
            "• `!sound help` — Show soundpad commands and audio usage\n"
            "• `!sound <name/id>` — Play sound effect or track in your voice channel\n"
            "• `!sound list` — View available audio clips (alias: `!s l`)\n"
            "• `!sound stop` — Stop sound playback and leave voice"
        ),
        inline=False
    )

    # 5. ADMINISTRATION
    embed.add_field(
        name="⚙️ Administration (`!adm` / `!a`)",
        value=(
            "• `!adm help` — Open detailed administrator tools panel (alias: `!a h`)\n"
            "• `!adm clear <n>` — Delete recent channel messages\n"
            "• `!adm exp <amount> [user]` — Add or remove user XP\n"
            "• `!adm exp_update` — Fix XP float rounding and recalculate levels (alias: `!a e_u`)"
        ),
        inline=False
    )

    embed.set_footer(
        text=f"Requested by {ctx.author.display_name}",
        icon_url=ctx.author.display_avatar.url
    )

    await ctx.send(embed=embed)

EXTENSIONS = [
    "utils.commands.commands_cog",
    "utils.event.event_cog",
    "utils.slash_commands.slash_commands_cog"
]

for ext in EXTENSIONS:
    bot.load_extension(ext)

if __name__ == "__main__":
    TOKEN_FILE = "txt.jpg"

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            bot_token = f.read().strip()
    else:
        print(f"Error: Token file '{TOKEN_FILE}' not found!")
        sys.exit(1)

    try:
        bot.run(bot_token)
    finally:
        if getattr(bot, "is_restarting", False):
            print("Spawning process...")
            subprocess.run([sys.executable, *sys.argv])