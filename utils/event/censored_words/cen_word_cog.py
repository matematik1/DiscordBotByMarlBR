from utils.config import CENSORED_WORDS
import disnake
from disnake.ext import commands


class CensoredWords(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        content_lower = message.content.lower()

        if "!" in content_lower or "." in content_lower:
            return

        for word in CENSORED_WORDS:
            if word.lower() in content_lower:
                try:
                    await message.delete()

                    await message.channel.send(
                        f"Yo {message.author.mention}, don't call him that a fucking Skeeter.",
                        delete_after=5.0
                    )
                except disnake.Forbidden:
                    print(f"ADMIN PIDORAS DAI PRAVA")
                except disnake.HTTPException as e:
                    print(f"HTTP EROR: {e}")

                break

        if "ame" in content_lower or "аме" in content_lower:
            try:
                await message.delete()

                await message.channel.send(
                    f"Oh, my beloved Ame he's not The International champion again; he's second once more.",
                    delete_after=3.0
                )
            except disnake.Forbidden:
                print(f"ADMIN PIDORAS DAI PRAVA")
            except disnake.HTTPException as e:
                print(f"HTTP EROR: {e}")
    
def setup(bot: commands.Bot):
    bot.add_cog(CensoredWords(bot))