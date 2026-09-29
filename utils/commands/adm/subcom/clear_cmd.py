import disnake
from disnake.ext import commands

async def handle_clear(ctx: commands.Context, amount: int = 10):
    if amount <= 0:
        await ctx.send("The number of messages must be greater than 0")
        return
    if amount > 150:
        await ctx.send("You can delete a maximum of 150 messages at a time")
        return

    # +1 щоб видалити ще й саме повідомлення з командою !a c
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Cleared **{len(deleted) - 1}** messages", delete_after=3)