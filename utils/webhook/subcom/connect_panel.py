import disnake
from utils.webhook.helpers import create_connect_embed
from utils.webhook.views import ConnectProfileView


async def handle_connect_panel(
    inter: disnake.ApplicationCommandInteraction,
    target_channel: disnake.TextChannel,
    lang: str,
):
  await inter.response.defer(ephemeral=True)

  embed, file = create_connect_embed(lang)
  view = ConnectProfileView()

  if file:
    await target_channel.send(embed=embed, file=file, view=view)
  else:
    await target_channel.send(embed=embed, view=view)

  await inter.followup.send(
      f"✅ Panel has been sent to {target_channel.mention}!", ephemeral=True
  )