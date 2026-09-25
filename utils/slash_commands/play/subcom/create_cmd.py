import disnake
from ..helpers import LobbyView

async def handle_create_party(
    inter: disnake.ApplicationCommandInteraction,
    game: str,
    mode: str,
    slots: int,
    mmr: str,
    pos: str
):
    if slots < 2 or slots > 10:
        await inter.response.send_message("❌ Party size must be between 2 and 10 players!", ephemeral=True)
        return

    view = LobbyView(
        leader=inter.author,
        game=game,
        mode=mode,
        max_slots=slots,
        target_mmr=mmr,
        position=pos
    )

    await inter.response.send_message(embed=view.build_embed(), view=view)