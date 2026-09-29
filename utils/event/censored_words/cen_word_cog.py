from .words.censored_words import CENSORED_WORDS
from .words.troll_words import TROLL_WORDS
from utils.config import SANE_ROLE_ID, TROLL_ROLE_ID
import disnake
from disnake.ext import commands
import random
import re
import asyncio

class CensoredWords(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return
        if message.author.guild_permissions.administrator:
            return
        if any(role.id == SANE_ROLE_ID for role in message.author.roles):
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

        content_lower = message.content.lower().strip()

        normalized_content = re.sub(
            r"[!?.,]+$",
            "",
            content_lower
        ).strip()

        for trigger, responses in TROLL_WORDS.items():

            if normalized_content == trigger.lower():

                try:
                    if any(role.id != TROLL_ROLE_ID for role in message.author.roles):
                        try:
                            await message.author.add_roles(TROLL_ROLE_ID)
                        except Exception as e:
                            print(f"Error in given troll role: {e}")

                    response = random.choice(responses)

                    await message.channel.send(
                        f"{message.author.mention} {response}",
                        delete_after=5.0
                    )

                    await asyncio.sleep(5)
                    try:
                        await message.delete()
                    except disnake.NotFound:
                        pass

                except disnake.Forbidden:
                    print("ADMIN PIDORAS DAI PRAVA")

                except disnake.HTTPException as e:
                    print(f"HTTP ERROR: {e}")

                return
    
def setup(bot: commands.Bot):
    bot.add_cog(CensoredWords(bot))