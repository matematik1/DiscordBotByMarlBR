import disnake


class DotaLinksView(disnake.ui.View):
    def __init__(self, d2pt_slug: str, dotabuff_slug: str):
        super().__init__(timeout=None)

        self.add_item(
            disnake.ui.Button(
                label="Dota2ProTracker",
                url=f"https://dota2protracker.com/hero/{d2pt_slug}",
            )
        )

        self.add_item(
            disnake.ui.Button(
                label="Dotabuff",
                url=f"https://www.dotabuff.com/heroes/{dotabuff_slug}"
            )
        )