import nextcord
from nextcord.ext import commands

from config import WELCOME_CHANNEL_ID


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
            activity=nextcord.Activity(type=nextcord.ActivityType.listening, name="mokea.dev")
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


def setup(bot):
    bot.add_cog(Events(bot))
