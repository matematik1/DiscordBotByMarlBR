import disnake
from ..helpers import sync_all_guild_dota_roles

async def handle_sync_roles(inter: disnake.ApplicationCommandInteraction):
    await inter.response.defer(ephemeral=True)

    updated, failed = await sync_all_guild_dota_roles(inter.guild)

    embed = disnake.Embed(
        title="🔄 Dota 2 Role Sync Complete",
        description=(
            f"Bulk role sync finished for **{inter.guild.name}**:\n\n"
            f"• 🟢 **Successfully updated:** `{updated}` members\n"
            f"• 🟡 **Skipped / Unchanged:** `{failed}` members"
        ),
        color=disnake.Color.blue()
    )
    await inter.followup.send(embed=embed, ephemeral=True)