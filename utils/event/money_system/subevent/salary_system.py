import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import disnake
from disnake.ext import commands, tasks

from utils.config import TROLL_ROLE_ID
from utils.event.money_system.helpers import SALARY_CONFIG
from utils.storage import add_user_money

SALARY_STATE_FILE = Path("data") / "salary_claims.json"


def _load_claims() -> set[str]:
    SALARY_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not SALARY_STATE_FILE.exists():
        return set()
    try:
        data = json.loads(SALARY_STATE_FILE.read_text(encoding="utf-8"))
        return set(data) if isinstance(data, list) else set()
    except (OSError, json.JSONDecodeError):
        return set()


def _save_claims(claims: set[str]) -> None:
    SALARY_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Keep only recent claims. Four salary slots per day are enough to
    # preserve a few weeks of restart protection without growing forever.
    if len(claims) > 10000:
        claims = set(sorted(claims)[-5000:])

    SALARY_STATE_FILE.write_text(
        json.dumps(sorted(claims), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


class SalarySystem(commands.Cog):
    """Role-based scheduled salary system.

    A payment is made once per configured time/role/user/day. Claims are
    persisted so restarting the bot cannot pay the same salary twice.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.claims = _load_claims()
        self._last_minute: str | None = None

    def cog_load(self):
        if not self.salary_check_loop.is_running():
            self.salary_check_loop.start()

    def cog_unload(self):
        if self.salary_check_loop.is_running():
            self.salary_check_loop.cancel()

    @tasks.loop(seconds=30)
    async def salary_check_loop(self):
        now = datetime.now(ZoneInfo("Europe/Kyiv"))
        minute_key = now.strftime("%Y-%m-%d %H:%M")

        # Several loop ticks can happen during the same minute.
        if self._last_minute == minute_key:
            return
        self._last_minute = minute_key

        for setting in SALARY_CONFIG:
            if setting["time"] != now.strftime("%H:%M"):
                continue

            role_id = int(setting["role_id"])
            amount = int(setting["amount"])
            day = now.strftime("%Y-%m-%d")

            # One user may be present in multiple guilds. Pay once globally.
            members_by_id: dict[int, disnake.Member] = {}
            for guild in self.bot.guilds:
                for member in guild.members:
                    if member.bot:
                        continue
                    if any(role.id == TROLL_ROLE_ID for role in member.roles):
                        continue
                    if any(role.id == role_id for role in member.roles):
                        members_by_id.setdefault(member.id, member)

            changed = False
            for member_id, member in members_by_id.items():
                claim_key = f"{day}|{setting['time']}|{role_id}|{member_id}"
                if claim_key in self.claims:
                    continue

                try:
                    add_user_money(member_id, amount, member.display_name)
                    self.claims.add(claim_key)
                    changed = True
                except Exception as exc:
                    print(f"[Salary] Failed for {member_id}: {exc!r}")

            if changed:
                _save_claims(self.claims)

    @salary_check_loop.before_loop
    async def before_salary_check_loop(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(SalarySystem(bot))
