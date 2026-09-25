import os
import io
import aiohttp
import disnake
from utils.storage import save_user_steam_id
import urllib.parse
from PIL import Image
from utils.config import HEROES_GIF_DIR, HERO_NAME_OVERRIDES, ITEMS_B_DIR, ITEMS_I_DIR

def get_available_heroes():
    if not os.path.exists(HEROES_GIF_DIR):
        return []

    heroes = []
    prefix_double = "npc_dota_hero_npc_dota_hero_"
    prefix_single = "npc_dota_hero_"

    for filename in os.listdir(HEROES_GIF_DIR):
        if filename.lower().endswith(".gif"):
            clean_name = filename[:-4]

            if clean_name.startswith(prefix_double):
                clean_name = clean_name[len(prefix_double):]
            elif clean_name.startswith(prefix_single):
                clean_name = clean_name[len(prefix_single):]

            if clean_name in HERO_NAME_OVERRIDES:
                display_name = HERO_NAME_OVERRIDES[clean_name]
            else:
                display_name = clean_name.replace("_", " ").title()

            d2pt_slug = urllib.parse.quote(display_name)
            clean_dotabuff = display_name.lower().replace("'", "").replace(" ", "-")

            heroes.append({
                "name": display_name,
                "d2pt_slug": d2pt_slug,
                "dotabuff_slug": clean_dotabuff,
                "file_path": os.path.join(HEROES_GIF_DIR, filename),
                "file_name": filename
            })

    return heroes

def generate_inventory_image(boot_num: int, item_nums: list[int]) -> io.BytesIO:
    image_paths = [os.path.join(ITEMS_B_DIR, f"{boot_num}.png")]
    for num in item_nums:
        image_paths.append(os.path.join(ITEMS_I_DIR, f"{num}.png"))

    images = [Image.open(path).convert("RGBA") for path in image_paths]

    target_height = 80
    resized_images = []
    for img in images:
        w_percent = target_height / float(img.size[1])
        new_width = int(float(img.size[0]) * float(w_percent))
        resized_images.append(img.resize((new_width, target_height), Image.Resampling.LANCZOS))

    padding = 10
    total_width = sum(img.size[0] for img in resized_images) + padding * (len(resized_images) - 1)
    total_height = target_height

    inventory_canvas = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

    current_x = 0
    for img in resized_images:
        inventory_canvas.paste(img, (current_x, 0), img)
        current_x += img.size[0] + padding

    buffer = io.BytesIO()
    inventory_canvas.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

import aiohttp
import disnake
from utils.storage import save_user_steam_id
from utils.config import STEAM_API_KEY

class VerifySteamView(disnake.ui.View):
    def __init__(self, author_id: int, account_id: int, verify_code: str):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.account_id = account_id
        self.verify_code = verify_code

    @disnake.ui.button(label="✅ Verify Account", style=disnake.ButtonStyle.success)
    async def verify_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        if inter.author.id != self.author_id:
            await inter.response.send_message("❌ This verification is not for you!", ephemeral=True)
            return

        await inter.response.defer()

        steam_id_64 = self.account_id + 76561197960265728

        url = (
            f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            f"?key={STEAM_API_KEY}&steamids={steam_id_64}"
        )

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=10) as resp:
                    if resp.status != 200:
                        print(f"Error: Steam API returned status {resp.status}")
                        await inter.followup.send(f"❌ Steam API error (HTTP {resp.status}).", ephemeral=True)
                        return
                    data = await resp.json()
            except Exception as e:
                print(f"Error connecting to Steam API: {e}")
                await inter.followup.send("❌ Error connecting to Steam API. Try again later.", ephemeral=True)
                return

        players = data.get("response", {}).get("players", [])
        if not players:
            await inter.followup.send("❌ Steam profile not found. Please verify the entered ID.", ephemeral=True)
            return

        player = players[0]
        steam_name = player.get("personaname", "Steam User")
        real_name = player.get("realname", "")

        if self.verify_code in real_name or self.verify_code in steam_name:
            save_user_steam_id(
                discord_id=self.author_id,
                discord_name=inter.author.name,
                account_id=self.account_id,
                steam_name=steam_name
            )

            for child in self.children:
                child.disabled = True
            button.label = "Verified"
            await inter.edit_original_response(view=self)

            await inter.followup.send(
                f"🎉 **Success!** Account **{steam_name}** (`{self.account_id}`) has been linked to your Discord profile!\n"
                f"You can now revert your original Steam name.",
                ephemeral=True
            )
            self.stop()
        else:
            await inter.followup.send(
                f"❌ Verification code `{self.verify_code}` not found!\n"
                f"**Current Real Name:** `{real_name if real_name else 'empty'}`\n\n"
                f"👉 Paste `{self.verify_code}` into the **Real Name** field in your Steam profile settings, click **Save**, and press the button again.",
                ephemeral=True
            )

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

TIER_MAP = {
    1: "Herald",
    2: "Guardian",
    3: "Crusader",
    4: "Archon",
    5: "Legend",
    6: "Ancient",
    7: "Divine",
    8: "Immortal"
}

def format_rank_tier(tier: int | None) -> str:
    if not tier:
        return "Uncalibrated"
    if tier >= 80:
        return "Immortal 🏆"
    division = tier // 10
    stars = tier % 10
    name = TIER_MAP.get(division, "Unknown")
    return f"{name} [{stars}★]"

class ProfileLinksView(disnake.ui.View):
    def __init__(self, account_id: int):
        super().__init__(timeout=None)
        self.add_item(
            disnake.ui.Button(
                label="Dotabuff",
                url=f"https://www.dotabuff.com/players/{account_id}",
                style=disnake.ButtonStyle.link,
                emoji="📈"
            )
        )
        self.add_item(
            disnake.ui.Button(
                label="OpenDota",
                url=f"https://www.opendota.com/players/{account_id}",
                style=disnake.ButtonStyle.link,
                emoji="📊"
            )
        )
        self.add_item(
            disnake.ui.Button(
                label="Stratz",
                url=f"https://stratz.com/players/{account_id}",
                style=disnake.ButtonStyle.link,
                emoji="⚡"
            )
        )