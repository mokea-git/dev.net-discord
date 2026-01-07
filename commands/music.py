import nextcord
from nextcord.ext import commands
from nextcord.ui import View, Select
import yt_dlp
import aiohttp

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

# Discord Activity (Watch Together) ID
WATCH_TOGETHER_APP_ID = 880218394199220334


class MusicSelect(View):
    def __init__(self, cog):
        super().__init__(timeout=60)
        self.cog = cog

    @nextcord.ui.select(
        placeholder="기능을 선택하세요",
        options=[
            nextcord.SelectOption(label="On", description="음악 봇을 음성 채널에 입장시킵니다", emoji="🔊"),
            nextcord.SelectOption(label="Play", description="유튜브 링크로 음악을 재생합니다", emoji="▶️"),
            nextcord.SelectOption(label="Watch", description="Watch Together로 영상을 함께 봅니다", emoji="🎬"),
            nextcord.SelectOption(label="Off", description="음악을 멈추고 봇을 퇴장시킵니다", emoji="🔇"),
        ]
    )
    async def select_callback(self, select: nextcord.ui.Select, interaction: nextcord.Interaction):
        choice = select.values[0]

        if choice == "On":
            await interaction.response.send_modal(OnModal(self.cog))
        elif choice == "Play":
            await interaction.response.send_modal(PlayModal(self.cog))
        elif choice == "Watch":
            await interaction.response.send_modal(WatchModal(self.cog))
        elif choice == "Off":
            await interaction.response.send_modal(OffModal(self.cog))


class OnModal(nextcord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="음성 채널 입장")
        self.cog = cog

        self.confirm = nextcord.ui.TextInput(
            label="입장하려면 '시작'을 입력하세요",
            placeholder="시작",
            required=True,
            max_length=10
        )
        self.add_item(self.confirm)

    async def callback(self, interaction: nextcord.Interaction):
        if self.confirm.value != "시작":
            await interaction.response.send_message("'시작'을 입력해주세요.", ephemeral=True)
            return

        voice_channel = self.cog.bot.get_channel(MUSIC_VOICE_CHANNEL_ID)

        if voice_channel is None:
            await interaction.response.send_message("음성 채널을 찾을 수 없습니다.", ephemeral=True)
            return

        if interaction.guild.voice_client:
            await interaction.response.send_message("이미 음성 채널에 있습니다.", ephemeral=True)
            return

        await voice_channel.connect()
        await interaction.response.send_message(f"🔊 **{voice_channel.name}** 채널에 입장했습니다!", ephemeral=True)


class PlayModal(nextcord.ui.Modal):
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
        voice_client = interaction.guild.voice_client

        if not voice_client:
            await interaction.response.send_message("먼저 'On'으로 봇을 입장시켜주세요.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(self.url.value, download=False)
                url2 = info['url']
                title = info.get('title', '알 수 없는 제목')
                thumbnail = info.get('thumbnail', None)

            if voice_client.is_playing():
                voice_client.stop()

            source = nextcord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
            voice_client.play(source)

            embed = nextcord.Embed(
                title="▶️ 재생 중",
                description=f"**{title}**",
                color=nextcord.Color.red()
            )
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"오류가 발생했습니다: {e}", ephemeral=True)


class WatchModal(nextcord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="Watch Together")
        self.cog = cog

        self.confirm = nextcord.ui.TextInput(
            label="시작하려면 '시작'을 입력하세요",
            placeholder="시작",
            required=True,
            max_length=10
        )
        self.add_item(self.confirm)

    async def callback(self, interaction: nextcord.Interaction):
        if self.confirm.value != "시작":
            await interaction.response.send_message("'시작'을 입력해주세요.", ephemeral=True)
            return

        voice_channel = self.cog.bot.get_channel(MUSIC_VOICE_CHANNEL_ID)

        if voice_channel is None:
            await interaction.response.send_message("음성 채널을 찾을 수 없습니다.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Discord Activity 초대 링크 생성
            invite = await voice_channel.create_activity_invite(WATCH_TOGETHER_APP_ID)

            embed = nextcord.Embed(
                title="🎬 Watch Together",
                description=f"아래 링크를 클릭하여 함께 영상을 시청하세요!\n\n[**여기를 클릭하세요**]({invite.url})",
                color=nextcord.Color.blurple()
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/880218394199220334/ec48acbad4c32efab4275cb9f3ca3a58.png")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"오류가 발생했습니다: {e}", ephemeral=True)


class OffModal(nextcord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="음악 종료")
        self.cog = cog

        self.confirm = nextcord.ui.TextInput(
            label="종료하려면 '종료'를 입력하세요",
            placeholder="종료",
            required=True,
            max_length=10
        )
        self.add_item(self.confirm)

    async def callback(self, interaction: nextcord.Interaction):
        if self.confirm.value != "종료":
            await interaction.response.send_message("'종료'를 입력해주세요.", ephemeral=True)
            return

        voice_client = interaction.guild.voice_client

        if not voice_client:
            await interaction.response.send_message("봇이 음성 채널에 없습니다.", ephemeral=True)
            return

        if voice_client.is_playing():
            voice_client.stop()

        await voice_client.disconnect()
        await interaction.response.send_message("🔇 음악을 멈추고 퇴장했습니다.", ephemeral=True)


class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="music",
        description="음악 기능을 사용합니다",
        guild_ids=[GUILD_ID]
    )
    async def music(self, ctx: nextcord.Interaction):
        view = MusicSelect(self)
        await ctx.response.send_message("🎵 기능을 선택하세요:", view=view, ephemeral=True)


def setup(bot):
    bot.add_cog(MusicCommands(bot))
