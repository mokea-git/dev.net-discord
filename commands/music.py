import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
from nextcord.ui import View, Select
import yt_dlp
import asyncio

from config import GUILD_ID, MUSIC_VOICE_CHANNEL_ID

# yt-dlp 옵션
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class MusicSelect(View):
    def __init__(self, cog):
        super().__init__(timeout=60)
        self.cog = cog

    @nextcord.ui.select(
        placeholder="음악 기능을 선택하세요",
        options=[
            nextcord.SelectOption(label="On", description="음악 봇을 음성 채널에 입장시킵니다", emoji="🔊"),
            nextcord.SelectOption(label="Play", description="유튜브 링크로 음악을 재생합니다", emoji="▶️"),
            nextcord.SelectOption(label="Off", description="음악을 멈추고 봇을 퇴장시킵니다", emoji="🔇"),
        ]
    )
    async def select_callback(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        choice = select.values[0]

        if choice == "On":
            await self.cog.join_voice(interaction)
        elif choice == "Play":
            await self.cog.ask_youtube_url(interaction)
        elif choice == "Off":
            await self.cog.leave_voice(interaction)


class YouTubeURLModal(nextcord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="음악 재생")
        self.cog = cog

        self.url = nextcord.ui.TextInput(
            label="유튜브 링크",
            placeholder="https://www.youtube.com/watch?v=...",
            required=True
        )
        self.add_item(self.url)

    async def callback(self, interaction: nextcord.Interaction):
        await self.cog.play_music(interaction, self.url.value)


class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []
        self.is_playing = False

    async def join_voice(self, interaction: nextcord.Interaction):
        voice_channel = self.bot.get_channel(MUSIC_VOICE_CHANNEL_ID)

        if voice_channel is None:
            await interaction.response.send_message("음성 채널을 찾을 수 없습니다.", ephemeral=True)
            return

        if interaction.guild.voice_client:
            await interaction.response.send_message("이미 음성 채널에 있습니다.", ephemeral=True)
            return

        await voice_channel.connect()
        await interaction.response.send_message(f"🔊 **{voice_channel.name}** 채널에 입장했습니다!", ephemeral=True)

    async def ask_youtube_url(self, interaction: nextcord.Interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("먼저 'On'으로 봇을 입장시켜주세요.", ephemeral=True)
            return

        await interaction.response.send_modal(YouTubeURLModal(self))

    async def play_music(self, interaction: nextcord.Interaction, url: str):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            await interaction.response.send_message("봇이 음성 채널에 없습니다. 먼저 'On'을 선택하세요.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                title = info.get('title', '알 수 없는 제목')

            if voice_client.is_playing():
                voice_client.stop()

            source = nextcord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
            voice_client.play(source)

            await interaction.followup.send(f"▶️ 재생 중: **{title}**", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"오류가 발생했습니다: {e}", ephemeral=True)

    async def leave_voice(self, interaction: nextcord.Interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            await interaction.response.send_message("봇이 음성 채널에 없습니다.", ephemeral=True)
            return

        if voice_client.is_playing():
            voice_client.stop()

        await voice_client.disconnect()
        await interaction.response.send_message("🔇 음악을 멈추고 퇴장했습니다.", ephemeral=True)

    @nextcord.slash_command(
        name="music",
        description="음악 기능을 사용합니다",
        guild_ids=[GUILD_ID]
    )
    async def music(self, ctx: nextcord.Interaction):
        view = MusicSelect(self)
        await ctx.response.send_message("🎵 음악 기능을 선택하세요:", view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(MusicCommands(bot))
