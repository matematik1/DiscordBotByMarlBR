import disnake
import os

CONNECT_BANNER_COLOR = 0xEE3737
CONNECT_BANNER_RU = "CONNECTED_PANEL_IMG_RU.png"
CONNECT_BANNER_EU = "CONNECTED_PANEL_IMG_EU.png"

FOOTER_EN = (
    "Welcome to the server! Link your Steam account to unlock exclusive features, "
    "get automatic rank roles, and track your Dota 2 stats directly on the server.\n\n"
    "• Automatic Rank Roles — Your server role will automatically update based on your in-game Dota 2 medal and MMR.\n\n"
    "• Match & Profile Tracking — Access interactive commands to view your recent matches, win rates, and favorite heroes.\n\n"
    "• Leaderboards & Activity — Compete with other members on the server leaderboard and participate in community matches!\n\n"
    "To connect your account and access private channels, press the button below.\n\n"
    ":3"
)

FOOTER_RU = (
    "Добро пожаловать на сервер! Привяжите свой аккаунт Steam, чтобы открыть доступ к эксклюзивным функциям, "
    "автоматически получать роли в соответствии с рангом и отслеживать статистику Dota 2 прямо на сервере.\n\n"
    "• Автоматические роли по рангу — Ваша роль на сервере будет обновляться автоматически в зависимости от вашего внутриигрового ранга и MMR в Dota 2.\n\n"
    "• Отслеживание матчей и профиля — Используйте интерактивные команды для просмотра недавних матчей, процента побед и любимых героев.\n\n"
    "• Таблицы лидеров и активность — Соревнуйтесь с другими участниками в таблице лидеров сервера и участвуйте в матчах сообщества!\n\n"
    "Чтобы привязать аккаунт и получить доступ к закрытым каналам, нажмите кнопку ниже.\n\n"
    ":3"
)

def create_connect_embed(lang: str = "en") -> disnake.Embed:
    desc = FOOTER_RU if lang.lower() == "ru" else FOOTER_EN

    embed = disnake.Embed(
        color=CONNECT_BANNER_COLOR
    )

    embed.set_footer(text=desc)

    filename = (
      CONNECT_BANNER_RU if lang.lower() == "ru" else CONNECT_BANNER_EU
    )

    file_path = os.path.join("img", filename)
    file = None

    if os.path.exists(file_path):
        file = disnake.File(file_path, filename=filename)
        embed.set_image(url=f"attachment://{filename}")
    else:
        print(f"ERROR NOT FILE {file_path}")

    return embed, file