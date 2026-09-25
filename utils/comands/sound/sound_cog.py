import os
import asyncio
import disnake
from disnake.ext import commands
from utils.config import SOUND_DIR, SOUND_SUBCOMMANDS, FFMPEG_OPTIONS

class SoundCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["s"])
    async def sound(self, ctx: commands.Context, sound_name: str = None):
        if sound_name and sound_name.lower() in ("help", "h"):
            embed = disnake.Embed(
                title="🔊 Soundpad & Voice Audio",
                description="Play custom audio clips and sound effects directly in your voice channel:",
                color=disnake.Color.teal()
            )
            embed.add_field(
                name="• `!sound <name/id>`",
                value="> Play a specific sound effect from the soundboard",
                inline=False
            )
            embed.add_field(
                name="• `!sound list` (or `!s l`)",
                value="> Display all available sound files and their trigger IDs",
                inline=False
            )
            embed.add_field(
                name="• `!sound stop`",
                value="> Instantly stop the current sound and disconnect the bot",
                inline=False
            )
            embed.add_field(
                name="💡 Usage Notice",
                value="• You must be connected to a voice channel before using `!sound`\n• Aliases: `!s <sound>`",
                inline=False
            )
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )
            await ctx.send(embed=embed)
            return

        if sound_name and sound_name.lower() in ("list", "l"):
            if not os.path.exists(SOUND_DIR):
                await ctx.send("DIR NOT FOUND")
                return

            sounds = [file[:-4] for file in os.listdir(SOUND_DIR) if file.lower().endswith(".mp3")]
            if not sounds:
                await ctx.send("SOUND NOT FOUND")
                return

            sound_list_text = "\n".join(f"- `{name}`" for name in sorted(sounds))
            await ctx.send(f'ALL SOUND: \n{sound_list_text}')
            return

        if sound_name and sound_name.lower() in ("stop", "s"):
            voice_client: disnake.VoiceClient = ctx.voice_client
            if voice_client and voice_client.is_connected():
                if voice_client.is_playing():
                    voice_client.stop()
                await voice_client.disconnect()
                print("Sound Stoped")
            return

        if sound_name is None:
            await ctx.send("WRITE SOUND NAME")
            return

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("YOU NEED TO BE IN A VOICE CHANNEL")
            return

        target_channel = ctx.author.voice.channel
        if not sound_name.endswith(".mp3"):
            sound_name += ".mp3"

        file_path = os.path.join(SOUND_DIR, sound_name)
        if not os.path.exists(file_path):
            await ctx.send("SOUND NOT FOUND")
            return

        voice_client: disnake.VoiceClient = ctx.voice_client
        if voice_client is None:
            voice_client = await target_channel.connect()
        elif voice_client.channel != target_channel:
            await voice_client.move_to(target_channel)

        if voice_client.is_playing():
            voice_client.stop()

        def after_playing(error):
            if error:
                print(f'Error: {error}')

            async def disconnect_safely():
                await asyncio.sleep(0.5)
                if voice_client.is_connected() and not voice_client.is_playing():
                    await voice_client.disconnect()

            self.bot.loop.create_task(disconnect_safely())

        raw_source = disnake.FFmpegPCMAudio(file_path, **FFMPEG_OPTIONS)
        source = disnake.PCMVolumeTransformer(raw_source, volume=1.0)
        voice_client.play(source, after=after_playing)

def setup(bot: commands.Bot):
    bot.add_cog(SoundCog(bot))