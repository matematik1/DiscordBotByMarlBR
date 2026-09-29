import random
import disnake
import urllib.parse

from utils.commands.dota.helpers import get_available_heroes
from ..views import DotaLinksView


async def handle_hero(ctx):
    available_heroes = get_available_heroes()

    if not available_heroes:
        await ctx.send("❌ HERO FILE NOT FOUND.")
        return

    hero = random.choice(available_heroes)

    gif_file = disnake.File(
        hero["file_path"],
        filename=hero["file_name"]
    )

    embed = disnake.Embed(
        title=f"🎭 Random Hero: {hero['name']}",
        description=f"You rolled **{hero['name']}**!",
        color=disnake.Color.dark_red()
    )

    embed.set_image(url=f"attachment://{hero['file_name']}")

    hero_name = hero["name"]
    
    d2pt_slug = urllib.parse.quote(
        hero_name.lower().replace(" ", "-")
    )

    dotabuff_slug = urllib.parse.quote(
        hero_name.lower().replace(" ", "-")
    )

    view = DotaLinksView(
        d2pt_slug=d2pt_slug,
        dotabuff_slug=dotabuff_slug
    )

    await ctx.send(
        embed=embed,
        file=gif_file,
        view=view
    )