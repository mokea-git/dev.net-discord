import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
from nextcord.ui import Button, View
from datetime import datetime, timedelta
import sys
import os

from config import (
    GUILD_ID, ADMIN_ROLE_ID, ANNOUNCE_CHANNEL_ID,
    PUNISH_LOG_CHANNEL_ID, ROLE_ID
)


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = {}

    # ─────────────────────────
    # 재시작 (관리자)
    # ─────────────────────────
    @nextcord.slash_command(
        name="restart",
        description="봇을 재시작합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def restart(self, ctx: nextcord.Interaction):
        await ctx.response.send_message("🔄 봇을 재시작합니다...", ephemeral=True)
        os.execv(sys.executable, ['python'] + sys.argv)

    # ─────────────────────────
    # 인증
    # ─────────────────────────
    @nextcord.slash_command(
        name="check",
        description="MASTER CHECK",
        default_member_permissions=nextcord.Permissions(administrator=True)
    )
    async def check(self, ctx: nextcord.Interaction):
        role = ctx.guild.get_role(ROLE_ID)

        if role is None:
            await ctx.response.send_message("역할을 찾을 수 없습니다.", ephemeral=True)
            return

        button = Button(label="확인", style=nextcord.ButtonStyle.green)

        async def hi_callback(interaction: nextcord.Interaction):
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                "확인되었습니다. 역할이 지급되었습니다 ✅",
                ephemeral=True
            )

        button.callback = hi_callback
        view = View(timeout=180)
        view.add_item(button)

        await ctx.response.send_message(
            "내용을 모두 읽었다면 아래 버튼을 눌러주세요.",
            view=view
        )

    # ─────────────────────────
    # 공지 시스템
    # ─────────────────────────
    @nextcord.slash_command(
        name="공지",
        description="공지를 작성합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def announce(
        self,
        ctx: nextcord.Interaction,
        제목: str = SlashOption(description="공지 제목"),
        내용: str = SlashOption(description="공지 내용")
    ):
        channel = ctx.guild.get_channel(ANNOUNCE_CHANNEL_ID)
        if channel is None:
            await ctx.response.send_message("공지 채널을 찾을 수 없습니다.", ephemeral=True)
            return

        embed = nextcord.Embed(
            title=f"📢 {제목}",
            description=내용,
            color=nextcord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"작성자: {ctx.user.name}")

        await channel.send(embed=embed)
        await ctx.response.send_message(f"공지가 전송되었습니다! 👉 {channel.mention}", ephemeral=True)

    # ─────────────────────────
    # 임베드 생성기
    # ─────────────────────────
    @nextcord.slash_command(
        name="임베드",
        description="커스텀 임베드를 생성합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def embed_create(
        self,
        ctx: nextcord.Interaction,
        제목: str = SlashOption(description="임베드 제목"),
        내용: str = SlashOption(description="임베드 내용"),
        색상: str = SlashOption(
            description="색상 선택",
            choices={"빨강": "red", "파랑": "blue", "초록": "green", "노랑": "yellow", "보라": "purple"}
        )
    ):
        colors = {
            "red": nextcord.Color.red(),
            "blue": nextcord.Color.blue(),
            "green": nextcord.Color.green(),
            "yellow": nextcord.Color.gold(),
            "purple": nextcord.Color.purple()
        }

        embed = nextcord.Embed(
            title=제목,
            description=내용,
            color=colors.get(색상, nextcord.Color.blue())
        )

        await ctx.response.send_message(embed=embed)

    # ─────────────────────────
    # 추방 (관리자)
    # ─────────────────────────
    @nextcord.slash_command(
        name="추방",
        description="유저를 추방합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def kick(
        self,
        ctx: nextcord.Interaction,
        유저: nextcord.Member = SlashOption(description="추방할 유저"),
        사유: str = SlashOption(description="추방 사유", required=False, default="사유 없음")
    ):
        if 유저.top_role >= ctx.user.top_role:
            await ctx.response.send_message("자신보다 높거나 같은 역할의 유저는 추방할 수 없습니다.", ephemeral=True)
            return

        try:
            dm_embed = nextcord.Embed(
                title="👢 추방되었습니다",
                description=f"**{ctx.guild.name}** 서버에서 추방되었습니다.",
                color=nextcord.Color.orange()
            )
            dm_embed.add_field(name="사유", value=사유, inline=False)
            await 유저.send(embed=dm_embed)
        except:
            pass

        await 유저.kick(reason=사유)

        embed = nextcord.Embed(
            title="👢 추방 완료",
            color=nextcord.Color.orange()
        )
        embed.add_field(name="추방된 유저", value=f"{유저.name}#{유저.discriminator}", inline=True)
        embed.add_field(name="사유", value=사유, inline=True)
        embed.add_field(name="처리자", value=ctx.user.mention, inline=True)

        await ctx.response.send_message(embed=embed)

        log_channel = ctx.guild.get_channel(PUNISH_LOG_CHANNEL_ID)
        if log_channel:
            log_embed = nextcord.Embed(
                title="👢 추방",
                description=f"**{유저.name}**님이 추방되었습니다.",
                color=nextcord.Color.orange(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="대상", value=f"{유저.name}#{유저.discriminator}", inline=True)
            log_embed.add_field(name="처리자", value=ctx.user.mention, inline=True)
            log_embed.add_field(name="사유", value=사유, inline=False)
            await log_channel.send(embed=log_embed)

    # ─────────────────────────
    # 밴 (관리자)
    # ─────────────────────────
    @nextcord.slash_command(
        name="밴",
        description="유저를 밴합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def ban(
        self,
        ctx: nextcord.Interaction,
        유저: nextcord.Member = SlashOption(description="밴할 유저"),
        사유: str = SlashOption(description="밴 사유", required=False, default="사유 없음")
    ):
        if 유저.top_role >= ctx.user.top_role:
            await ctx.response.send_message("자신보다 높거나 같은 역할의 유저는 밴할 수 없습니다.", ephemeral=True)
            return

        try:
            dm_embed = nextcord.Embed(
                title="🔨 밴되었습니다",
                description=f"**{ctx.guild.name}** 서버에서 밴되었습니다.",
                color=nextcord.Color.red()
            )
            dm_embed.add_field(name="사유", value=사유, inline=False)
            await 유저.send(embed=dm_embed)
        except:
            pass

        await 유저.ban(reason=사유)

        embed = nextcord.Embed(
            title="🔨 밴 완료",
            color=nextcord.Color.red()
        )
        embed.add_field(name="밴된 유저", value=f"{유저.name}#{유저.discriminator}", inline=True)
        embed.add_field(name="사유", value=사유, inline=True)
        embed.add_field(name="처리자", value=ctx.user.mention, inline=True)

        await ctx.response.send_message(embed=embed)

        log_channel = ctx.guild.get_channel(PUNISH_LOG_CHANNEL_ID)
        if log_channel:
            log_embed = nextcord.Embed(
                title="🔨 밴",
                description=f"**{유저.name}**님이 밴되었습니다.",
                color=nextcord.Color.red(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="대상", value=f"{유저.name}#{유저.discriminator}", inline=True)
            log_embed.add_field(name="처리자", value=ctx.user.mention, inline=True)
            log_embed.add_field(name="사유", value=사유, inline=False)
            await log_channel.send(embed=log_embed)

    # ─────────────────────────
    # 언밴 (관리자)
    # ─────────────────────────
    @nextcord.slash_command(
        name="언밴",
        description="유저의 밴을 해제합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def unban(
        self,
        ctx: nextcord.Interaction,
        유저id: str = SlashOption(description="언밴할 유저의 ID")
    ):
        try:
            user = await self.bot.fetch_user(int(유저id))
            await ctx.guild.unban(user)

            embed = nextcord.Embed(
                title="✅ 언밴 완료",
                color=nextcord.Color.green()
            )
            embed.add_field(name="언밴된 유저", value=f"{user.name}#{user.discriminator}", inline=True)
            embed.add_field(name="처리자", value=ctx.user.mention, inline=True)

            await ctx.response.send_message(embed=embed)

            log_channel = ctx.guild.get_channel(PUNISH_LOG_CHANNEL_ID)
            if log_channel:
                log_embed = nextcord.Embed(
                    title="✅ 언밴",
                    description=f"**{user.name}**님의 밴이 해제되었습니다.",
                    color=nextcord.Color.green(),
                    timestamp=datetime.now()
                )
                log_embed.add_field(name="대상", value=f"{user.name}#{user.discriminator}", inline=True)
                log_embed.add_field(name="처리자", value=ctx.user.mention, inline=True)
                await log_channel.send(embed=log_embed)

        except ValueError:
            await ctx.response.send_message("올바른 유저 ID를 입력해주세요.", ephemeral=True)
        except nextcord.NotFound:
            await ctx.response.send_message("해당 유저를 찾을 수 없거나 밴 목록에 없습니다.", ephemeral=True)
        except Exception as e:
            await ctx.response.send_message(f"오류가 발생했습니다: {e}", ephemeral=True)

    # ─────────────────────────
    # 타임아웃 (관리자)
    # ─────────────────────────
    @nextcord.slash_command(
        name="타임아웃",
        description="유저를 타임아웃합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def timeout(
        self,
        ctx: nextcord.Interaction,
        유저: nextcord.Member = SlashOption(description="타임아웃할 유저"),
        시간: int = SlashOption(description="타임아웃 시간(분)", min_value=1, max_value=40320),
        사유: str = SlashOption(description="타임아웃 사유", required=False, default="사유 없음")
    ):
        if 유저.top_role >= ctx.user.top_role:
            await ctx.response.send_message("자신보다 높거나 같은 역할의 유저는 타임아웃할 수 없습니다.", ephemeral=True)
            return

        await ctx.response.defer()

        duration = timedelta(minutes=시간)
        await 유저.timeout(duration, reason=사유)

        try:
            dm_embed = nextcord.Embed(
                title="🔇 타임아웃되었습니다",
                description=f"**{ctx.guild.name}** 서버에서 타임아웃되었습니다.",
                color=nextcord.Color.dark_gray()
            )
            dm_embed.add_field(name="시간", value=f"{시간}분", inline=True)
            dm_embed.add_field(name="사유", value=사유, inline=False)
            await 유저.send(embed=dm_embed)
        except:
            pass

        embed = nextcord.Embed(
            title="🔇 타임아웃 완료",
            color=nextcord.Color.dark_gray()
        )
        embed.add_field(name="타임아웃된 유저", value=유저.mention, inline=True)
        embed.add_field(name="시간", value=f"{시간}분", inline=True)
        embed.add_field(name="사유", value=사유, inline=False)
        embed.set_footer(text=f"처리자: {ctx.user.name}")

        await ctx.followup.send(embed=embed)

        log_channel = ctx.guild.get_channel(PUNISH_LOG_CHANNEL_ID)
        if log_channel:
            log_embed = nextcord.Embed(
                title="🔇 타임아웃",
                description=f"**{유저.name}**님이 타임아웃되었습니다.",
                color=nextcord.Color.dark_gray(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="대상", value=유저.mention, inline=True)
            log_embed.add_field(name="시간", value=f"{시간}분", inline=True)
            log_embed.add_field(name="처리자", value=ctx.user.mention, inline=True)
            log_embed.add_field(name="사유", value=사유, inline=False)
            await log_channel.send(embed=log_embed)

    # ─────────────────────────
    # 경고 시스템
    # ─────────────────────────
    @nextcord.slash_command(
        name="경고",
        description="유저에게 경고를 부여합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def warn(
        self,
        ctx: nextcord.Interaction,
        유저: nextcord.Member = SlashOption(description="경고할 유저"),
        사유: str = SlashOption(description="경고 사유", required=False, default="사유 없음")
    ):
        user_id = str(유저.id)

        if user_id not in self.warnings:
            self.warnings[user_id] = []

        self.warnings[user_id].append({
            "reason": 사유,
            "by": ctx.user.name,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        warn_count = len(self.warnings[user_id])

        try:
            dm_embed = nextcord.Embed(
                title="⚠️ 경고를 받았습니다",
                description=f"**{ctx.guild.name}** 서버에서 경고를 받았습니다.",
                color=nextcord.Color.orange()
            )
            dm_embed.add_field(name="사유", value=사유, inline=False)
            dm_embed.add_field(name="누적 경고", value=f"{warn_count}회", inline=True)
            await 유저.send(embed=dm_embed)
        except:
            pass

        embed = nextcord.Embed(
            title="⚠️ 경고",
            color=nextcord.Color.orange()
        )
        embed.add_field(name="경고 받은 유저", value=유저.mention, inline=True)
        embed.add_field(name="누적 경고", value=f"{warn_count}회", inline=True)
        embed.add_field(name="사유", value=사유, inline=False)
        embed.set_footer(text=f"처리자: {ctx.user.name}")

        await ctx.response.send_message(embed=embed)

        log_channel = ctx.guild.get_channel(PUNISH_LOG_CHANNEL_ID)
        if log_channel:
            log_embed = nextcord.Embed(
                title="⚠️ 경고",
                description=f"**{유저.name}**님이 경고를 받았습니다.",
                color=nextcord.Color.orange(),
                timestamp=datetime.now()
            )
            log_embed.add_field(name="대상", value=유저.mention, inline=True)
            log_embed.add_field(name="누적 경고", value=f"{warn_count}회", inline=True)
            log_embed.add_field(name="처리자", value=ctx.user.mention, inline=True)
            log_embed.add_field(name="사유", value=사유, inline=False)
            await log_channel.send(embed=log_embed)

        if warn_count >= 3:
            await ctx.channel.send(f"⚠️ {유저.mention}님이 경고 {warn_count}회에 도달했습니다!")

    @nextcord.slash_command(
        name="경고확인",
        description="유저의 경고 내역을 확인합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def warn_check(
        self,
        ctx: nextcord.Interaction,
        유저: nextcord.Member = SlashOption(description="확인할 유저")
    ):
        user_id = str(유저.id)

        if user_id not in self.warnings or len(self.warnings[user_id]) == 0:
            await ctx.response.send_message(f"{유저.mention}님은 경고가 없습니다.", ephemeral=True)
            return

        embed = nextcord.Embed(
            title=f"⚠️ {유저.name}의 경고 내역",
            color=nextcord.Color.orange()
        )

        for i, warn in enumerate(self.warnings[user_id], 1):
            embed.add_field(
                name=f"경고 {i}",
                value=f"사유: {warn['reason']}\n처리자: {warn['by']}\n시간: {warn['time']}",
                inline=False
            )

        await ctx.response.send_message(embed=embed)

    @nextcord.slash_command(
        name="경고초기화",
        description="유저의 경고를 초기화합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def warn_reset(
        self,
        ctx: nextcord.Interaction,
        유저: nextcord.Member = SlashOption(description="초기화할 유저")
    ):
        user_id = str(유저.id)

        if user_id in self.warnings:
            del self.warnings[user_id]

        await ctx.response.send_message(f"{유저.mention}님의 경고가 초기화되었습니다.", ephemeral=True)


def setup(bot):
    bot.add_cog(AdminCommands(bot))
