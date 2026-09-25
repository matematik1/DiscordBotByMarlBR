import random
import disnake
from utils.config import DOTA_POSITIONS, HEROES_GIF_DIR
from ..helpers import get_available_heroes, generate_inventory_image

async def handle_random(inter: disnake.ApplicationCommandInteraction):
    await inter.response.defer()

    available_heroes = get_available_heroes()
    if not available_heroes:
        await inter.followup.send(f"Error: No hero GIF files found in `{HEROES_GIF_DIR}`.", ephemeral=True)
        return

    hero_data = random.choice(available_heroes)
    position = random.choice(DOTA_POSITIONS)
    boot_id = random.randint(1, 5)
    chosen_items = random.sample(list(range(1, 64)), 5)

    try:
        inv_buffer = generate_inventory_image(boot_id, chosen_items)
    except Exception as e:
        await inter.followup.send(f"Error generating item layout: {e}", ephemeral=True)
        return

    hero_file = disnake.File(hero_data["file_path"], filename="hero.gif")
    inventory_file = disnake.File(fp=inv_buffer, filename="inventory.png")

    embed = disnake.Embed(
        title=f"🎲 Hero Roulette: {hero_data['name']}",
        description=f"📍 **Position:** `{position}`\n🎒 **RANDOM Item Build:**",
        color=disnake.Color.gold(),
    )
    embed.set_thumbnail(url="attachment://hero.gif")
    embed.set_image(url="attachment://inventory.png")
    embed.set_footer(text=f"Rolled by {inter.author.display_name}", icon_url=inter.author.display_avatar.url)

    await inter.followup.send(embed=embed, files=[hero_file, inventory_file])