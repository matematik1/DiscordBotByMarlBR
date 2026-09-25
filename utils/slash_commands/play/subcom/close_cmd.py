import disnake

async def handle_close_room(inter: disnake.ApplicationCommandInteraction):
    if not inter.author.voice or not inter.author.voice.channel:
        await inter.response.send_message("⚠️ You must be connected to a voice channel to close it!", ephemeral=True)
        return

    channel = inter.author.voice.channel

    try:
        await channel.delete(reason=f"Closed by party leader {inter.author.name}")
        await inter.response.send_message(f"🗑️ Party room **{channel.name}** was deleted.", ephemeral=True)
    except disnake.Forbidden:
        await inter.response.send_message("❌ Bot lacks permission to delete this channel.", ephemeral=True)
    except disnake.NotFound:
        await inter.response.send_message("❌ Channel already deleted.", ephemeral=True)