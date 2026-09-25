import disnake
from disnake.ext import commands

async def handle_close_room(ctx: commands.Context):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("⚠️ You must be connected to the party voice channel to close it!")
        return

    channel = ctx.author.voice.channel
    if not channel.name.startswith("🔊 Party:"):
        await ctx.send("❌ You can only close temporary channels starting with `🔊 Party:`!")
        return

    try:
        await channel.delete(reason=f"Closed by party leader {ctx.author.name}")
        await ctx.send(f"🗑️ Party room **{channel.name}** was deleted.")
    except disnake.Forbidden:
        await ctx.send("❌ Bot lacks permission to delete this channel.")
    except disnake.NotFound:
        pass