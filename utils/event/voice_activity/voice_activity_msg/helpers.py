from datetime import datetime
from zoneinfo import ZoneInfo

import disnake

from utils.config import VOICE_ACTIVITY_CHANNEL_ID


EVENTS = {
    "connect": {
        "title": "🔊 Зашёл в голосовой канал",
        "color": disnake.Color.green(),
    },
    "disconnect": {
        "title": "🔇 Вышел из голосового канала",
        "color": disnake.Color.red(),
    },
    "transfer": {
        "title": "🔄 Перешёл в другой голосовой канал",
        "color": disnake.Color.blurple(),
    },
}


async def send_voice_log(
    bot: disnake.Client,
    member: disnake.Member,
    action: str,
    event_type: str,
    channel_name: str,
    previous_channel: str | None = None,
):
    channel = bot.get_channel(VOICE_ACTIVITY_CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(
                VOICE_ACTIVITY_CHANNEL_ID
            )
        except (disnake.NotFound, disnake.Forbidden):
            print("[VoiceActivity] Не удалось получить канал логов.")
            return
        except disnake.HTTPException as error:
            print(f"[VoiceActivity] Ошибка Discord API: {error}")
            return

    if not hasattr(channel, "send"):
        print("[VoiceActivity] Канал логов не поддерживает отправку сообщений.")
        return

    event = EVENTS.get(event_type)

    if event is None:
        print(f"[VoiceActivity] Неизвестный тип события: {event_type}")
        return

    now = datetime.now(ZoneInfo("Europe/Malta"))

    embed = disnake.Embed(
        title=event["title"],
        color=event["color"],
        timestamp=now,
    )

    embed.set_author(
        name=member.display_name,
        icon_url=member.display_avatar.url,
    )

    if event_type == "transfer" and previous_channel:
        embed.add_field(
            name="Откуда",
            value=f"🔊 {previous_channel}",
            inline=True,
        )
        embed.add_field(
            name="Куда",
            value=f"🔊 {channel_name}",
            inline=True,
        )
    else:
        embed.add_field(
            name="Голосовой канал",
            value=f"🔊 {channel_name}",
            inline=False,
        )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=f"Voice Activity • ID: {member.id}"
    )

    await channel.send(
        embed=embed,
        allowed_mentions=disnake.AllowedMentions.none(),
    )