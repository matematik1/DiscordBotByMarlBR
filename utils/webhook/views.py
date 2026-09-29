import random
import disnake
from utils.commands.dota.helpers import VerifySteamView  # підключаємо твою в'юшку


class ConnectModal(disnake.ui.Modal):
    def __init__(self):
        # 1. Поле для вводу
        input_field = disnake.ui.TextInput(
            label="Steam ID",
            placeholder="Enter your Steam ID or Friend ID (e.g. 123456789)",
            custom_id="my_steam_id",
            style=disnake.TextInputStyle.short,
            min_length=3,
            max_length=32,
            required=True,
        )

        # 2. Налаштування вікна
        super().__init__(
            title="Account connection",
            custom_id="connect_steam_modal_window",
            components=[input_field],
        )

    # 3. Callback на рівні класу, а не всередині __init__!
    async def callback(self, inter: disnake.ModalInteraction):
        raw_id = inter.text_values["my_steam_id"].strip()

        # Відповідаємо приховано (щоб ніхто не бачив код верифікації в загальному чаті)
        await inter.response.defer(ephemeral=True)

        # Перевіряємо, чи ввів користувач числа
        try:
            account_id = int(raw_id)
            # Якщо раптом ввели повний SteamID64 (більше ніж 76561197960265728)
            if account_id > 76561197960265728:
                account_id -= 76561197960265728
        except ValueError:
            await inter.followup.send(
                "❌ Please enter a valid numeric Steam ID or Friend ID (numbers only)!",
                ephemeral=True,
            )
            return

        # Генеруємо код підтвердження так само, як у твоїй команді handle_connect
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
            color=disnake.Color.blue(),
        )
        embed.set_footer(text="You have 3 minutes to complete verification.")

        # Викликаємо твоє готове VerifySteamView!
        view = VerifySteamView(
            author_id=inter.author.id,
            account_id=account_id,
            verify_code=verify_code,
        )
        await inter.followup.send(embed=embed, view=view, ephemeral=True)

class ConnectProfileView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Connect profile",
        style=disnake.ButtonStyle.danger,
        custom_id="unique_id_here",
        emoji="🛡️"
    )
    async def connect_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(ConnectModal())

    @disnake.ui.button(
        label="Where to find your ID?",
        style=disnake.ButtonStyle.secondary,
        custom_id="btn_help_id",
        emoji="❓"
    )
    async def help_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        help_text = (
            "**How to find your Steam ID:**\n"
            "1. Open Dota 2 -> Your profile -> button next to nickname (friend ID).\n"
            "2. Or go to your Steam profile in a browser and copy the link or the number from the address."
        )
        await inter.response.send_message(help_text, ephemeral=True)