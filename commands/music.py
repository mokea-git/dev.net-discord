import nextcord
from nextcord.ext import commands
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


class MusicModal(nextcord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="음악 기능")
        self.cog = cog

        self.action = nextcord.ui.TextInput(
            label="기능 선택 (on / off / play / watch)",
            placeholder="on, off, play, watch 중 하나를 입력하세요",
            required=True,
            max_length=10
        )
        self.add_item(self.action)

        self.url = nextcord.ui.TextInput(
            label="유튜브 링크 (play 선택 시에만 입력)",
            placeholder="https://www.youtube.com/watch?v=...",
            required=False
        )
        self.add_item(self.url)

    async def callback(self, interaction: nextcord.Interaction):
        action = self.action.value.lower().strip()

        if action == "on":
            await self.handle_on(interaction)
        elif action == "off":
            await self.handle_off(interaction)
        elif action == "play":
            await self.handle_play(interaction)
        elif action == "watch":
            await self.handle_watch(interaction)
        else:
            await interaction.response.send_message(
                "❌ 올바른 기능을 입력해주세요: `on`, `off`, `play`, `watch`",
                ephemeral=True
            )

    async def handle_on(self, interaction: nextcord.Interaction):
        voice_channel = self.cog.bot.get_channel(MUSIC_VOICE_CHANNEL_ID)

        if voice_channel is None:
            await interaction.response.send_message("음성 채널을 찾을 수 없습니다.", ephemeral=True)
            return

        if interaction.guild.voice_client:
            await interaction.response.send_message("이미 음성 채널에 있습니다.", ephemeral=True)
            return

        await voice_channel.connect()
        await interaction.response.send_message(f"🔊 **{voice_channel.name}** 채널에 입장했습니다!", ephemeral=True)

    async def handle_off(self, interaction: nextcord.Interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            await interaction.response.send_message("봇이 음성 채널에 없습니다.", ephemeral=True)
            return

        if voice_client.is_playing():
            voice_client.stop()

        await voice_client.disconnect()
        await interaction.response.send_message("🔇 음악을 멈추고 퇴장했습니다.", ephemeral=True)

    async def handle_play(self, interaction: nextcord.Interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            await interaction.response.send_message("먼저 `on`으로 봇을 입장시켜주세요.", ephemeral=True)
            return

        if not self.url.value:
            await interaction.response.send_message("유튜브 링크를 입력해주세요.", ephemeral=True)
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

    async def handle_watch(self, interaction: nextcord.Interaction):
        voice_channel = self.cog.bot.get_channel(MUSIC_VOICE_CHANNEL_ID)

        if voice_channel is None:
            await interaction.response.send_message("음성 채널을 찾을 수 없습니다.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://discord.com/api/v10/channels/{voice_channel.id}/invites",
                    json={
                        "max_age": 86400,
                        "max_uses": 0,
                        "target_application_id": str(WATCH_TOGETHER_APP_ID),
                        "target_type": 2
                    },
                    headers={
                        "Authorization": f"Bot {self.cog.bot.http.token}",
                        "Content-Type": "application/json"
                    }
                ) as resp:
                    data = await resp.json()
                    invite_code = data.get("code")

            if not invite_code:
                await interaction.followup.send("초대 링크 생성에 실패했습니다.", ephemeral=True)
                return

            invite_url = f"https://discord.gg/{invite_code}"

            embed = nextcord.Embed(
                title="🎬 Watch Together",
                description=f"아래 링크를 클릭하여 함께 영상을 시청하세요!\n\n[**여기를 클릭하세요**]({invite_url})",
                color=nextcord.Color.blurple()
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"오류가 발생했습니다: {e}", ephemeral=True)


class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="music",
        description="음악 기능을 사용합니다",
        guild_ids=[GUILD_ID]
    )
    async def music(self, ctx: nextcord.Interaction):
        await ctx.response.send_modal(MusicModal(self))


def setup(bot):
    bot.add_cog(MusicCommands(bot))
