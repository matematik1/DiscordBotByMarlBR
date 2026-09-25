import random
import disnake
from ..helpers import VerifySteamView

async def handle_connect(inter: disnake.ApplicationCommandInteraction, account_id: int):
    verify_code = f"MarBR-{random.randint(1000, 9999)}"

    embed = disnake.Embed(
        title="🔗 Steam Account Linking",
        description=(
            f"To verify ownership of Dota account **`{account_id}`**:\n\n"
            f"1. Open **Edit Profile** in Steam.\n"
            f"2. Paste this code into your **Real Name** field:\n"
            f"👉 **`{verify_code}`**\n\n"
            f"3. Click **Save** in Steam.\n"
            f"4. Click the **Verify Account** button below."
        ),
        color=disnake.Color.blue()
    )
    embed.set_footer(text="You have 3 minutes to complete verification.")

    view = VerifySteamView(author_id=inter.author.id, account_id=account_id, verify_code=verify_code)
    await inter.response.send_message(embed=embed, view=view, ephemeral=True)