import random
import disnake

# --- ПУЛИ GIF-АНІМАЦІЙ ---
GIFS_DUEL_START = [
    "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExOW5uZ3B0ZXlqMWF1ZHdwd2dyNmxhZGVlczZ2bnBybjA2dWNnN2ltZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fX8771PO1eATJz6r4R/giphy.gif"
]

GIFS_DUEL_SHOOT = [
    "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExdmdvaTMwNWMxbGY3b2tycXB3Y2ZlbHRpZHM4dnduYmt1bDYzbjRwNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YXhAt49P3fVFA1AgaU/giphy.gif"
]

GIFS_ROULETTE_SPIN = [
    "https://i.gifer.com/MpGR.gif"
]

GIFS_ROULETTE_CLICK = [
    "https://i.gifer.com/OJMM.gif"
]

GIFS_ROULETTE_BANG = [
    "https://i.gifer.com/JHu2.gif"
]


class DuelInviteView(disnake.ui.View):
    """Панель підтвердження виклику на дуель для опонента."""
    def __init__(self, challenger: disnake.Member, opponent: disnake.Member):
        super().__init__(timeout=45.0)
        self.challenger = challenger
        self.opponent = opponent
        self.accepted = False

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

    @disnake.ui.button(label="Accept Duel", style=disnake.ButtonStyle.success, emoji="⚔️")
    async def accept_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id != self.opponent.id:
            await inter.response.send_message("❌ This duel invitation is not for you!", ephemeral=True)
            return

        self.accepted = True
        self.stop()
        await inter.response.defer()

    @disnake.ui.button(label="Decline", style=disnake.ButtonStyle.danger, emoji="🏳️")
    async def decline_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id != self.opponent.id:
            await inter.response.send_message("❌ This duel invitation is not for you!", ephemeral=True)
            return

        self.accepted = False
        self.stop()
        embed = disnake.Embed(
            title="🏳️ Duel Declined",
            description=f"{self.opponent.mention} declined the challenge from {self.challenger.mention}.",
            color=disnake.Color.dark_gray()
        )
        for item in self.children:
            item.disabled = True
        await inter.response.edit_message(embed=embed, view=self)


class RussianRouletteView(disnake.ui.View):
    """Покроковий барабан російської рулетки з чергою пострілів."""
    def __init__(self, p1: disnake.Member, p2: disnake.Member):
        super().__init__(timeout=60.0)
        self.p1 = p1
        self.p2 = p2
        self.turn = random.choice([p1, p2])
        self.cylinder = [0, 0, 0, 0, 0, 1]
        random.shuffle(self.cylinder)
        self.chamber_index = 0

    @disnake.ui.button(label="Pull Trigger", style=disnake.ButtonStyle.danger, emoji="🔫")
    async def trigger_btn(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id != self.turn.id:
            await inter.response.send_message(f"⏳ Wait for your turn! Now pulling: {self.turn.display_name}.", ephemeral=True)
            return

        is_bullet = self.cylinder[self.chamber_index] == 1
        self.chamber_index += 1

        if is_bullet:
            loser = self.turn
            winner = self.p2 if loser.id == self.p1.id else self.p1
            self.stop()

            embed = disnake.Embed(
                title="💥 *BANG!*",
                description=(
                    f"**Chamber {self.chamber_index}/6 was loaded!**\n\n"
                    f"💀 {loser.mention} pulled the trigger and lost.\n"
                    f"🏆 **Winner:** {winner.mention}"
                ),
                color=disnake.Color.dark_red()
            )
            embed.set_image(url=random.choice(GIFS_ROULETTE_BANG))
            embed.set_footer(text="Game Over")

            for item in self.children:
                item.disabled = True
            await inter.response.edit_message(embed=embed, view=self)

            try:
                await loser.timeout(duration=60, reason="Lost Russian Roulette")
            except Exception:
                pass
        else:
            self.turn = self.p2 if self.turn.id == self.p1.id else self.p1
            embed = disnake.Embed(
                title="*Click...* 💨",
                description=(
                    f"Chamber **{self.chamber_index}/6** was empty!\n"
                    f"The cylinder rotates... Next turn: **{self.turn.mention}**!"
                ),
                color=disnake.Color.dark_gold()
            )
            embed.set_image(url=random.choice(GIFS_ROULETTE_CLICK))
            embed.set_footer(text=f"Turn: {self.turn.display_name}")
            await inter.response.edit_message(embed=embed, view=self)