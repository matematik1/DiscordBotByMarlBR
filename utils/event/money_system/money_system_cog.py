from disnake.ext import commands


class MoneySystem(commands.Cog):
    """Container cog for the money module.

    SalarySystem is registered by event_cog. Keeping this cog lightweight
    avoids accidentally registering the salary task twice.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot


def setup(bot: commands.Bot):
    bot.add_cog(MoneySystem(bot))
