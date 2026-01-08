import nextcord
from nextcord.ext import commands
import yt_dlp
import asyncio

from config import GUILD_ID, MUSIC_VOICE_CHANNEL_ID, ADMIN_ROLE_ID

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


class MusicModal(nextcord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="음악 기능")
        self.cog = cog

        self.action = nextcord.ui.TextInput(
            label="기능 선택 (on / off / play / queue / skip / nowplaying / loop / volume)",
            placeholder="play, queue, skip, nowplaying, loop, volume",
            required=True,
            max_length=15
        )
        self.add_item(self.action)

        self.url = nextcord.ui.TextInput(
            label="유튜브 링크 (play/queue 시) 또는 설정값",
            placeholder="https://www.youtube.com/... 또는 loop: on/off, volume: 0-100",
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
        elif action == "queue":
            await self.handle_queue(interaction)
        elif action == "skip":
            await self.handle_skip(interaction)
        elif action == "nowplaying" or action == "np":
            await self.handle_nowplaying(interaction)
        elif action == "loop":
            await self.handle_loop(interaction)
        elif action == "volume":
            await self.handle_volume(interaction)
        else:
            await interaction.response.send_message(
                "❌ 올바른 기능을 입력해주세요: `on`, `off`, `play`, `queue`, `skip`, `nowplaying`, `loop`, `volume`",
                ephemeral=True
            )

    async def handle_on(self, interaction: nextcord.Interaction):
        # 관리자 확인
        if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("❌ 관리자만 사용할 수 있습니다.", ephemeral=True)
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

    async def handle_off(self, interaction: nextcord.Interaction):
        # 관리자 확인
        if not any(role.id == ADMIN_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("❌ 관리자만 사용할 수 있습니다.", ephemeral=True)
            return

        voice_client = interaction.guild.voice_client

        if not voice_client:
            await interaction.response.send_message("봇이 음성 채널에 없습니다.", ephemeral=True)
            return

        if voice_client.is_playing():
            voice_client.stop()

        # 재생목록 초기화
        self.cog.music_queue.clear()
        self.cog.current_song = None

        await voice_client.disconnect()
        await interaction.response.send_message("🔇 음악을 멈추고 퇴장했습니다.", ephemeral=True)

    async def handle_play(self, interaction: nextcord.Interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            await interaction.response.send_message("먼저 관리자가 `on`으로 봇을 입장시켜야 합니다.", ephemeral=True)
            return

        if not self.url.value:
            await interaction.response.send_message("유튜브 링크를 입력해주세요.", ephemeral=True)
            return

        await interaction.response.defer()

        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(self.url.value, download=False)
                url2 = info['url']
                title = info.get('title', '알 수 없는 제목')
                thumbnail = info.get('thumbnail', None)
                duration = info.get('duration', 0)

            song_data = {
                'url': url2,
                'title': title,
                'thumbnail': thumbnail,
                'duration': duration,
                'requester': interaction.user
            }

            # 현재 재생 중이면 큐에 추가
            if voice_client.is_playing():
                self.cog.music_queue.append(song_data)
                embed = nextcord.Embed(
                    title="➕ 재생목록에 추가됨",
                    description=f"**{title}**",
                    color=nextcord.Color.blue()
                )
                embed.add_field(name="대기열 위치", value=f"{len(self.cog.music_queue)}번째", inline=True)
                embed.set_footer(text=f"요청자: {interaction.user.name}")
                if thumbnail:
                    embed.set_thumbnail(url=thumbnail)
                await interaction.followup.send(embed=embed)
            else:
                # 즉시 재생
                self.cog.current_song = song_data
                await self.cog.play_song(voice_client, interaction.channel)

                embed = nextcord.Embed(
                    title="▶️ 재생 시작",
                    description=f"**{title}**",
                    color=nextcord.Color.green()
                )
                if thumbnail:
                    embed.set_thumbnail(url=thumbnail)
                embed.set_footer(text=f"요청자: {interaction.user.name}")
                await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"오류가 발생했습니다: {e}")

    async def handle_queue(self, interaction: nextcord.Interaction):
        if not self.cog.music_queue and not self.cog.current_song:
            await interaction.response.send_message("재생목록이 비어있습니다.", ephemeral=True)
            return

        embed = nextcord.Embed(
            title="🎵 재생목록",
            color=nextcord.Color.purple()
        )

        # 현재 재생 중인 곡
        if self.cog.current_song:
            embed.add_field(
                name="▶️ 현재 재생 중",
                value=f"**{self.cog.current_song['title']}**\n요청자: {self.cog.current_song['requester'].name}",
                inline=False
            )

        # 대기 중인 곡들
        if self.cog.music_queue:
            queue_text = ""
            for idx, song in enumerate(self.cog.music_queue[:10], 1):  # 최대 10개
                queue_text += f"`{idx}.` {song['title']}\n"

            embed.add_field(
                name=f"⏭️ 대기 중 ({len(self.cog.music_queue)}곡)",
                value=queue_text,
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def handle_skip(self, interaction: nextcord.Interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client or not voice_client.is_playing():
            await interaction.response.send_message("재생 중인 곡이 없습니다.", ephemeral=True)
            return

        voice_client.stop()  # 다음 곡이 자동으로 재생됨
        await interaction.response.send_message("⏭️ 다음 곡으로 넘어갑니다.")

    async def handle_nowplaying(self, interaction: nextcord.Interaction):
        if not self.cog.current_song:
            await interaction.response.send_message("재생 중인 곡이 없습니다.", ephemeral=True)
            return

        song = self.cog.current_song
        embed = nextcord.Embed(
            title="🎵 현재 재생 중",
            description=f"**{song['title']}**",
            color=nextcord.Color.green()
        )
        if song['thumbnail']:
            embed.set_thumbnail(url=song['thumbnail'])

        embed.add_field(name="요청자", value=song['requester'].mention, inline=True)

        if song['duration']:
            minutes = song['duration'] // 60
            seconds = song['duration'] % 60
            embed.add_field(name="길이", value=f"{minutes}:{seconds:02d}", inline=True)

        if self.cog.loop_mode:
            embed.add_field(name="반복재생", value="🔁 ON", inline=True)

        await interaction.response.send_message(embed=embed)

    async def handle_loop(self, interaction: nextcord.Interaction):
        if not self.url.value:
            # 토글
            self.cog.loop_mode = not self.cog.loop_mode
        else:
            value = self.url.value.lower().strip()
            if value == "on":
                self.cog.loop_mode = True
            elif value == "off":
                self.cog.loop_mode = False
            else:
                await interaction.response.send_message("❌ `on` 또는 `off`를 입력해주세요.", ephemeral=True)
                return

        status = "활성화" if self.cog.loop_mode else "비활성화"
        emoji = "🔁" if self.cog.loop_mode else "➡️"
        await interaction.response.send_message(f"{emoji} 반복재생이 **{status}**되었습니다.")

    async def handle_volume(self, interaction: nextcord.Interaction):
        if not self.url.value:
            await interaction.response.send_message(
                f"현재 볼륨: **{int(self.cog.volume * 100)}%**\n변경하려면 0-100 사이의 숫자를 입력하세요.",
                ephemeral=True
            )
            return

        try:
            volume = int(self.url.value)
            if volume < 0 or volume > 100:
                await interaction.response.send_message("볼륨은 0-100 사이의 값이어야 합니다.", ephemeral=True)
                return

            self.cog.volume = volume / 100

            voice_client = interaction.guild.voice_client
            if voice_client and voice_client.source:
                voice_client.source.volume = self.cog.volume

            await interaction.response.send_message(f"🔊 볼륨을 **{volume}%**로 설정했습니다.")

        except ValueError:
            await interaction.response.send_message("숫자를 입력해주세요.", ephemeral=True)


class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_queue = []
        self.current_song = None
        self.loop_mode = False
        self.volume = 0.5  # 기본 볼륨 50%

    async def play_song(self, voice_client, channel):
        """곡 재생"""
        if not self.current_song:
            return

        song = self.current_song

        def after_playing(error):
            if error:
                print(f"재생 오류: {error}")

            # 다음 곡 재생
            asyncio.run_coroutine_threadsafe(self.play_next(voice_client, channel), self.bot.loop)

        source = nextcord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS)
        source = nextcord.PCMVolumeTransformer(source, volume=self.volume)
        voice_client.play(source, after=after_playing)

    async def play_next(self, voice_client, channel):
        """다음 곡 재생"""
        # 반복재생이 켜져있고 현재 곡이 있으면 다시 재생
        if self.loop_mode and self.current_song:
            await self.play_song(voice_client, channel)
            return

        # 대기열에서 다음 곡 가져오기
        if self.music_queue:
            self.current_song = self.music_queue.pop(0)
            await self.play_song(voice_client, channel)

            # 다음 곡 알림
            embed = nextcord.Embed(
                title="▶️ 다음 곡 재생",
                description=f"**{self.current_song['title']}**",
                color=nextcord.Color.green()
            )
            if self.current_song['thumbnail']:
                embed.set_thumbnail(url=self.current_song['thumbnail'])
            embed.set_footer(text=f"요청자: {self.current_song['requester'].name}")
            await channel.send(embed=embed)
        else:
            self.current_song = None

    @nextcord.slash_command(
        name="music",
        description="음악 기능을 사용합니다",
        guild_ids=[GUILD_ID]
    )
    async def music(self, interaction: nextcord.Interaction):
        modal = MusicModal(self)
        await interaction.response.send_modal(modal)


def setup(bot):
    bot.add_cog(MusicCommands(bot))
