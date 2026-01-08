import nextcord
from nextcord.ext import commands

from config import WELCOME_CHANNEL_ID, EXTENDED_LOG_CHANNEL_ID


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ─────────────────────────
    # 봇 준비
    # ─────────────────────────
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"We have logged in as {self.bot.user}")
        await self.bot.change_presence(
            status=nextcord.Status.dnd,
            activity=nextcord.Activity(type=nextcord.ActivityType.listening, name="생각중...")
        )
        # ~~하는 중 등 상태 설정법
        # activity=nextcord.Game(name="하는 중")
        # activity=nextcord.Streaming(name="방송 중", url="올리고 싶은 URL")
        # activity=nextcord.Activity(type=nextcord.ActivityType.listening, name="듣는 중")
        # activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="시청 중")

    # ─────────────────────────
    # 환영 메시지
    # ─────────────────────────
    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if channel is None:
            return

        embed = nextcord.Embed(
            title="👋 환영합니다!",
            description=f"{member.mention}님이 서버에 입장했습니다!",
            color=nextcord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="멤버 수", value=f"{member.guild.member_count}명", inline=True)

        await channel.send(embed=embed)

    # ─────────────────────────
    # 퇴장 메시지
    # ─────────────────────────
    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if channel is None:
            return

        embed = nextcord.Embed(
            title="👋 안녕히 가세요",
            description=f"**{member.name}**님이 서버를 떠났습니다.",
            color=nextcord.Color.red()
        )

        await channel.send(embed=embed)

    # ─────────────────────────
    # 메시지 삭제 로그
    # ─────────────────────────
    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        # 봇 메시지 무시
        if message.author.bot:
            return

        log_channel = message.guild.get_channel(EXTENDED_LOG_CHANNEL_ID)
        if log_channel is None:
            return

        embed = nextcord.Embed(
            title="🗑️ 메시지 삭제됨",
            color=nextcord.Color.red(),
            timestamp=message.created_at
        )
        embed.add_field(name="작성자", value=message.author.mention, inline=True)
        embed.add_field(name="채널", value=message.channel.mention, inline=True)
        embed.add_field(name="내용", value=message.content[:1024] if message.content else "*내용 없음*", inline=False)

        if message.attachments:
            embed.add_field(
                name="첨부파일",
                value="\n".join([att.filename for att in message.attachments]),
                inline=False
            )

        await log_channel.send(embed=embed)

    # ─────────────────────────
    # 메시지 수정 로그
    # ─────────────────────────
    @commands.Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message):
        # 봇 메시지 무시
        if before.author.bot:
            return

        # 내용이 같으면 무시 (임베드 업데이트 등)
        if before.content == after.content:
            return

        log_channel = before.guild.get_channel(EXTENDED_LOG_CHANNEL_ID)
        if log_channel is None:
            return

        embed = nextcord.Embed(
            title="✏️ 메시지 수정됨",
            color=nextcord.Color.orange(),
            timestamp=after.edited_at
        )
        embed.add_field(name="작성자", value=before.author.mention, inline=True)
        embed.add_field(name="채널", value=before.channel.mention, inline=True)
        embed.add_field(name="수정 전", value=before.content[:1024] if before.content else "*내용 없음*", inline=False)
        embed.add_field(name="수정 후", value=after.content[:1024] if after.content else "*내용 없음*", inline=False)
        embed.add_field(name="메시지 링크", value=f"[바로가기]({after.jump_url})", inline=False)

        await log_channel.send(embed=embed)

    # ─────────────────────────
    # 멤버 업데이트 로그 (닉네임, 역할 변경)
    # ─────────────────────────
    @commands.Cog.listener()
    async def on_member_update(self, before: nextcord.Member, after: nextcord.Member):
        log_channel = before.guild.get_channel(EXTENDED_LOG_CHANNEL_ID)
        if log_channel is None:
            return

        # 닉네임 변경
        if before.display_name != after.display_name:
            embed = nextcord.Embed(
                title="👤 닉네임 변경",
                color=nextcord.Color.blue()
            )
            embed.add_field(name="유저", value=after.mention, inline=True)
            embed.add_field(name="변경 전", value=before.display_name, inline=True)
            embed.add_field(name="변경 후", value=after.display_name, inline=True)
            await log_channel.send(embed=embed)

        # 역할 변경
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]

            if added_roles or removed_roles:
                embed = nextcord.Embed(
                    title="🎭 역할 변경",
                    color=nextcord.Color.purple()
                )
                embed.add_field(name="유저", value=after.mention, inline=False)

                if added_roles:
                    embed.add_field(
                        name="추가된 역할",
                        value=" ".join([role.mention for role in added_roles]),
                        inline=False
                    )

                if removed_roles:
                    embed.add_field(
                        name="제거된 역할",
                        value=" ".join([role.mention for role in removed_roles]),
                        inline=False
                    )

                await log_channel.send(embed=embed)

    # ─────────────────────────
    # 음성 채널 활동 로그
    # ─────────────────────────
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
        log_channel = member.guild.get_channel(EXTENDED_LOG_CHANNEL_ID)
        if log_channel is None:
            return

        # 음성 채널 입장
        if before.channel is None and after.channel is not None:
            embed = nextcord.Embed(
                title="🔊 음성 채널 입장",
                description=f"{member.mention}님이 {after.channel.mention}에 입장했습니다.",
                color=nextcord.Color.green()
            )
            await log_channel.send(embed=embed)

        # 음성 채널 퇴장
        elif before.channel is not None and after.channel is None:
            embed = nextcord.Embed(
                title="🔇 음성 채널 퇴장",
                description=f"{member.mention}님이 {before.channel.mention}에서 퇴장했습니다.",
                color=nextcord.Color.red()
            )
            await log_channel.send(embed=embed)

        # 음성 채널 이동
        elif before.channel != after.channel and before.channel is not None and after.channel is not None:
            embed = nextcord.Embed(
                title="🔀 음성 채널 이동",
                description=f"{member.mention}님이 {before.channel.mention}에서 {after.channel.mention}로 이동했습니다.",
                color=nextcord.Color.blue()
            )
            await log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))
