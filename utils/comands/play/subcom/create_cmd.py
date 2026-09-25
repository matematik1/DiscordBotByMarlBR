import disnake
from disnake.ext import commands
from utils.comands.play.helpers import LobbyView

async def handle_create_party(ctx: commands.Context, args: tuple):
    # За замовчуванням
    game = "Dota 2"
    mode = "Ranked"
    slots = 5
    mmr = "Any"
    pos = "Any"

    # Гнучкий парсинг переданих аргументів
    if len(args) >= 1:
        game = args[0]
    if len(args) >= 2:
        mode = args[1]
    if len(args) >= 3:
        # Шукаємо кількість слотів
        try:
            slots = int(args[2])
            if slots < 2 or slots > 10:
                slots = 5
        except ValueError:
            pos = args[2]
    if len(args) >= 4:
        mmr = args[3]
    if len(args) >= 5:
        pos = args[4]

    view = LobbyView(
        leader=ctx.author,
        game=game,
        mode=mode,
        max_slots=slots,
        target_mmr=mmr,
        position=pos
    )

    await ctx.send(embed=view.build_embed(), view=view)