import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import time

from config import GUILD_ID


class GeneralCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ─────────────────────────
    # 핑
    # ─────────────────────────
    @nextcord.slash_command(
        name="핑",
        description="봇의 응답 속도를 확인합니다",
        guild_ids=[GUILD_ID]
    )
    async def ping(self, ctx: nextcord.Interaction):
        latency = round(self.bot.latency * 1000)
        await ctx.response.send_message(f"🏓 퐁! `{latency}ms`")

    # ─────────────────────────
    # 봇 정보
    # ─────────────────────────
    @nextcord.slash_command(
        name="정보",
        description="봇 정보를 확인합니다",
        guild_ids=[GUILD_ID]
    )
    async def botinfo(self, ctx: nextcord.Interaction):
        embed = nextcord.Embed(
            title="DEV.NET",
            description="서버 관리를 위한 다목적 봇입니다.",
            color=nextcord.Color.blurple()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="개발자", value="mokea", inline=True)
        embed.add_field(name="버전", value="1.0.0", inline=True)
        embed.add_field(
            name="링크",
            value="[웹사이트](https://mokea.dev)",
            inline=False
        )

        await ctx.response.send_message(embed=embed)

    # ─────────────────────────
    # 유저 정보
    # ─────────────────────────
    @nextcord.slash_command(
        name="유저정보",
        description="유저 정보를 조회합니다",
        guild_ids=[GUILD_ID]
    )
    async def userinfo(
        self,
        ctx: nextcord.Interaction,
        유저: nextcord.Member = SlashOption(description="조회할 유저", required=False)
    ):
        user = 유저 or ctx.user

        embed = nextcord.Embed(
            title=f"👤 {user.name} 정보",
            color=user.color
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="닉네임", value=user.display_name, inline=True)
        embed.add_field(name="계정 생성일", value=user.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="서버 가입일", value=user.joined_at.strftime("%Y-%m-%d"), inline=True)

        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        embed.add_field(
            name=f"역할 ({len(roles)}개)",
            value=" ".join(roles) if roles else "없음",
            inline=False
        )

        await ctx.response.send_message(embed=embed)

    # ─────────────────────────
    # 서버 정보
    # ─────────────────────────
    @nextcord.slash_command(
        name="서버정보",
        description="서버 정보를 조회합니다",
        guild_ids=[GUILD_ID]
    )
    async def serverinfo(self, ctx: nextcord.Interaction):
        guild = ctx.guild

        embed = nextcord.Embed(
            title=f"🏠 {guild.name}",
            color=nextcord.Color.green()
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="서버 ID", value=guild.id, inline=True)
        embed.add_field(name="서버 주인", value=guild.owner.mention, inline=True)
        embed.add_field(name="생성일", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="멤버 수", value=f"{guild.member_count}명", inline=True)
        embed.add_field(name="채널 수", value=f"{len(guild.channels)}개", inline=True)
        embed.add_field(name="역할 수", value=f"{len(guild.roles)}개", inline=True)

        await ctx.response.send_message(embed=embed)

    # ─────────────────────────
    # 아바타
    # ─────────────────────────
    @nextcord.slash_command(
        name="아바타",
        description="유저의 프로필 사진을 확인합니다",
        guild_ids=[GUILD_ID]
    )
    async def avatar(
        self,
        ctx: nextcord.Interaction,
        유저: nextcord.Member = SlashOption(description="확인할 유저", required=False)
    ):
        user = 유저 or ctx.user
        embed = nextcord.Embed(
            title=f"🖼️ {user.name}의 아바타",
            color=user.color
        )
        embed.set_image(url=user.display_avatar.url)
        await ctx.response.send_message(embed=embed)

    # ─────────────────────────
    # 도움말
    # ─────────────────────────
    @nextcord.slash_command(
        name="도움말",
        description="사용 가능한 명령어 목록을 확인합니다",
        guild_ids=[GUILD_ID]
    )
    async def help(self, ctx: nextcord.Interaction):
        embed = nextcord.Embed(
            title="📖 명령어 목록",
            color=nextcord.Color.blurple()
        )
        embed.add_field(
            name="일반",
            value="`/핑` `/정보` `/도움말` `/아바타` `/유저정보` `/서버정보`",
            inline=False
        )
        embed.add_field(
            name="관리자",
            value="`/공지` `/임베드` `/추방` `/밴` `/언밴` `/타임아웃` `/경고` `/경고확인` `/경고초기화` `/restart`",
            inline=False
        )
        embed.add_field(
            name="티켓",
            value="`/ticket` `/신고`",
            inline=False
        )
        embed.add_field(
            name="음악",
            value="`/music`",
            inline=False
        )
        await ctx.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
