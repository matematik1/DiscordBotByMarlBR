import disnake

async def handle_close_room(inter: disnake.ApplicationCommandInteraction):
    # Якщо користувач перебуває у тимчасовому голосовому каналі
    if not inter.author.voice or not inter.author.voice.channel:
        await inter.response.send_message("⚠️ You must be connected to the voice channel you want to close!", ephemeral=True)
        return

    channel = inter.author.voice.channel

    # Перевірка, що це саме тимчасова кімната
    if not channel.name.startswith("🔊 Party:"):
        await inter.response.send_message("❌ You can only close temporary party channels!", ephemeral=True)
        return

    try:
        await channel.delete(reason=f"Closed by party leader {inter.author.name}")
        await inter.response.send_message(f"🗑️ Party room **{channel.name}** was deleted.", ephemeral=True)
    except disnake.Forbidden:
        await inter.response.send_message("❌ Bot lacks permission to delete this channel.", ephemeral=True)