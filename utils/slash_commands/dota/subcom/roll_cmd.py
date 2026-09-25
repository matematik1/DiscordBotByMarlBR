import os
import random
import asyncio
import disnake

async def handle_roll(inter: disnake.ApplicationCommandInteraction, min_val: int, max_val: int):
    if min_val >= max_val:
        max_val = min_val + 1

    anim_embed = disnake.Embed(
        title="🎲 Rolling the dice...",
        description="> *Shaking the cup...* ⏳",
        color=disnake.Color.dark_gray()
    )
    anim_embed.set_author(name=f"{inter.author.display_name} is rolling...", icon_url=inter.author.display_avatar.url)

    await inter.response.send_message(embed=anim_embed)

    dice_frames = ["🎲", "♥️", "🧩", "🎴", "🎰", "🎱", "🪩"]
    for _ in range(3):
        await asyncio.sleep(0.45)
        fake_num = random.randint(min_val, max_val)
        anim_embed.description = f"> *Rolling...* {random.choice(dice_frames)} **[{fake_num}]**"
        await inter.edit_original_response(embed=anim_embed)

    number = random.randint(min_val, max_val)
    gif_filename = "luck_cat.gif"
    gif_path = os.path.join("video", gif_filename)

    final_embed = disnake.Embed(
        title="🎲 Roll Results 🎲",
        description=(
            "> *A roll for those without chat in Dota 2!*\n\n"
            f"**Range:** `{min_val} – {max_val}`\n"
            f"**Rolled:** 🎯 **{number}**"
        ),
        color=disnake.Color.gold()
    )
    final_embed.set_author(name=f"{inter.author.display_name} rolled the dice", icon_url=inter.author.display_avatar.url)
    final_embed.set_footer(text="May the roll gods be on your side")

    if os.path.exists(gif_path):
        file = disnake.File(gif_path, filename=gif_filename)
        final_embed.set_thumbnail(url=f"attachment://{gif_filename}")
        await inter.channel.send(file=file, embed=final_embed)
        await inter.delete_original_response()
    else:
        await inter.edit_original_response(embed=final_embed)