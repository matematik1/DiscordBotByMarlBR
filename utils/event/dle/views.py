import disnake
from disnake.ui import View, Button
from .helpers import HeroInfo


class DLEView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.guess_button = Button(
            label="Guess the Hero",
            style=disnake.ButtonStyle.primary,
            custom_id="dle:guess"
        )

        self.guess_button.callback = self.guess_callback
        self.add_item(self.guess_button)

    async def guess_callback(self, inter: disnake.MessageInteraction):
        await inter.response.send_message(
            "🎯 You can choose a hero here: ",
            view=DLEHeroSelect(heroes=HeroInfo),
            ephemeral=True
        )

class DLEHeroSelect(disnake.ui.StringSelect):
    def __init__(self, heroes):
        options = [
            disnake.SelectOption(label=hero["championName"], value=str(hero["heroId"]))
            for hero in heroes
        ]
        super().__init__(
            placeholder="Select a hero...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="dle:hero_select"
        )

    async def callback(self, inter: disnake.MessageInteraction):
        selected_hero_id = int(self.values[0])
        await inter.response.send_message(
            f"You selected hero ID: {selected_hero_id}",
            ephemeral=True
        )