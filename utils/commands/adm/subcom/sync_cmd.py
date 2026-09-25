import disnake
from disnake.ext import commands
from ..helpers import sync_all_guild_dota_roles

async def handle_sync_roles(ctx: commands.Context):
    msg = await ctx.send("🔄 Synchronizing Dota 2 rank roles for all members, please wait...")
    
    updated, failed = await sync_all_guild_dota_roles(ctx.guild)

    embed = disnake.Embed(
        title="🔄 Dota 2 Role Sync Complete",
        description=(
            f"Role sync finished for **{ctx.guild.name}**:\n\n"
            f"• 🟢 **Successfully updated:** `{updated}` members\n"
            f"• 🟡 **Skipped / Unchanged:** `{failed}` members"
        ),
        color=disnake.Color.blue()
    )
    await msg.edit(content=None, embed=embed)