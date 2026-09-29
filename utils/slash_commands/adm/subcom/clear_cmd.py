import disnake

async def handle_clear(inter: disnake.ApplicationCommandInteraction, amount: int = 10):
    if amount <= 0:
        await inter.response.send_message("The number of messages must be greater than 0", ephemeral=True)
        return
    if amount > 150:
        await inter.response.send_message("You can delete a maximum of 150 messages at a time", ephemeral=True)
        return

    # Відкладаємо відповідь, щоб бот встиг видалити повідомлення
    await inter.response.defer(ephemeral=True)
    
    deleted = await inter.channel.purge(limit=amount)
    
    await inter.edit_original_response(content=f"Cleared **{len(deleted)}** messages")