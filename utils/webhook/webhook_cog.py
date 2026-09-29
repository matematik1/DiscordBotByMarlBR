import disnake
from disnake.ext import commands

from utils.webhook.subcom.connect_panel import handle_connect_panel
from utils.webhook.views import ConnectProfileView


class WebhookCog(commands.Cog):

  def __init__(self, bot: commands.Bot):
    self.bot = bot

  def cog_load(self):
    self.bot.add_view(ConnectProfileView())

  @commands.slash_command(
      name="webhook",
      description="Webhook and panel tools",
      default_member_permissions=disnake.Permissions(administrator=True),
  )
  async def webhook(self, inter: disnake.ApplicationCommandInteraction):
    pass

  @webhook.sub_command(
      name="panel", description="Sends the connect panel to the selected chat"
  )
  async def panel(
      self,
      inter: disnake.ApplicationCommandInteraction,
      target_channel: disnake.TextChannel = commands.Param(
          description="Select the chat to which the message will be sent"
      ),
      lang: str = commands.Param(
          default="en", description="Choose language", choices=["en", "ru"]
      ),
  ):
    await handle_connect_panel(inter, target_channel, lang)


def setup(bot: commands.Bot):
    bot.add_cog(WebhookCog(bot))