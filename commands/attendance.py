import nextcord
from nextcord.ext import commands
import json
import os
from datetime import datetime

from config import GUILD_ID, ATTENDANCE_CHANNEL_ID


class Attendance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "attendance_data.json"
        self.attendance_data = self.load_data()

    def load_data(self):
        """출석 데이터 로드"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_data(self):
        """출석 데이터 저장"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.attendance_data, f, ensure_ascii=False, indent=2)

    def get_user_data(self, user_id: str):
        """유저 데이터 가져오기"""
        if user_id not in self.attendance_data:
            self.attendance_data[user_id] = {
                "total_days": 0,
                "points": 0,
                "last_attendance": None,
                "streak": 0
            }
        return self.attendance_data[user_id]

    # ─────────────────────────
    # 출석체크
    # ─────────────────────────
    @nextcord.slash_command(
        name="출석",
        description="일일 출석체크를 합니다",
        guild_ids=[GUILD_ID]
    )
    async def attendance(self, ctx: nextcord.Interaction):
        user_id = str(ctx.user.id)
        user_data = self.get_user_data(user_id)

        today = datetime.now().strftime("%Y-%m-%d")

        # 오늘 이미 출석했는지 확인
        if user_data["last_attendance"] == today:
            embed = nextcord.Embed(
                title="❌ 이미 출석했습니다",
                description="내일 다시 출석해주세요!",
                color=nextcord.Color.red()
            )
            embed.add_field(name="총 출석일", value=f"{user_data['total_days']}일", inline=True)
            embed.add_field(name="포인트", value=f"{user_data['points']}P", inline=True)
            embed.add_field(name="연속 출석", value=f"{user_data['streak']}일", inline=True)
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        # 연속 출석 계산
        yesterday = datetime.strptime(today, "%Y-%m-%d")
        yesterday = yesterday.replace(day=yesterday.day - 1).strftime("%Y-%m-%d")

        if user_data["last_attendance"] == yesterday:
            user_data["streak"] += 1
        else:
            user_data["streak"] = 1

        # 출석 보상 계산 (연속 출석 보너스)
        base_points = 10
        bonus_points = min(user_data["streak"] * 2, 50)  # 최대 50 보너스
        total_points = base_points + bonus_points

        # 데이터 업데이트
        user_data["total_days"] += 1
        user_data["points"] += total_points
        user_data["last_attendance"] = today

        self.save_data()

        # 출석 완료 메시지
        embed = nextcord.Embed(
            title="✅ 출석 완료!",
            description=f"{ctx.user.mention}님 출석을 완료했습니다!",
            color=nextcord.Color.green()
        )
        embed.add_field(name="획득 포인트", value=f"+{total_points}P", inline=True)
        embed.add_field(name="연속 출석", value=f"{user_data['streak']}일 🔥", inline=True)
        embed.add_field(name="", value="", inline=False)  # 줄바꿈
        embed.add_field(name="총 출석일", value=f"{user_data['total_days']}일", inline=True)
        embed.add_field(name="보유 포인트", value=f"{user_data['points']}P", inline=True)

        if bonus_points > 0:
            embed.set_footer(text=f"연속 출석 보너스: +{bonus_points}P")

        await ctx.response.send_message(embed=embed)

        # 출석 채널에도 공지
        attendance_channel = ctx.guild.get_channel(ATTENDANCE_CHANNEL_ID)
        if attendance_channel:
            simple_embed = nextcord.Embed(
                description=f"✅ {ctx.user.mention}님이 출석했습니다! ({user_data['streak']}일 연속)",
                color=nextcord.Color.green()
            )
            await attendance_channel.send(embed=simple_embed)

    # ─────────────────────────
    # 출석 현황
    # ─────────────────────────
    @nextcord.slash_command(
        name="출석현황",
        description="나의 출석 현황을 확인합니다",
        guild_ids=[GUILD_ID]
    )
    async def attendance_status(self, ctx: nextcord.Interaction):
        user_id = str(ctx.user.id)
        user_data = self.get_user_data(user_id)

        embed = nextcord.Embed(
            title=f"📊 {ctx.user.name}님의 출석 현황",
            color=nextcord.Color.blue()
        )
        embed.set_thumbnail(url=ctx.user.display_avatar.url)
        embed.add_field(name="총 출석일", value=f"{user_data['total_days']}일", inline=True)
        embed.add_field(name="연속 출석", value=f"{user_data['streak']}일 🔥", inline=True)
        embed.add_field(name="보유 포인트", value=f"{user_data['points']}P", inline=True)

        if user_data["last_attendance"]:
            embed.add_field(
                name="마지막 출석",
                value=user_data["last_attendance"],
                inline=False
            )

        await ctx.response.send_message(embed=embed, ephemeral=True)

    # ─────────────────────────
    # 출석 랭킹
    # ─────────────────────────
    @nextcord.slash_command(
        name="출석랭킹",
        description="출석 랭킹을 확인합니다",
        guild_ids=[GUILD_ID]
    )
    async def attendance_ranking(self, ctx: nextcord.Interaction):
        # 포인트 기준으로 정렬
        sorted_users = sorted(
            self.attendance_data.items(),
            key=lambda x: x[1]["points"],
            reverse=True
        )[:10]  # 상위 10명

        if not sorted_users:
            await ctx.response.send_message("아직 출석한 사람이 없습니다.", ephemeral=True)
            return

        embed = nextcord.Embed(
            title="🏆 출석 랭킹 (상위 10명)",
            description="포인트 기준 랭킹입니다.",
            color=nextcord.Color.gold()
        )

        medals = ["🥇", "🥈", "🥉"]

        for idx, (user_id, data) in enumerate(sorted_users):
            try:
                user = await self.bot.fetch_user(int(user_id))
                medal = medals[idx] if idx < 3 else f"{idx + 1}."

                embed.add_field(
                    name=f"{medal} {user.name}",
                    value=f"포인트: {data['points']}P | 출석: {data['total_days']}일 | 연속: {data['streak']}일",
                    inline=False
                )
            except:
                pass

        await ctx.response.send_message(embed=embed)

    # ─────────────────────────
    # 출석 포인트 관리 (관리자 전용)
    # ─────────────────────────
    @nextcord.slash_command(
        name="포인트관리",
        description="유저의 출석 포인트를 관리합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def manage_points(
        self,
        ctx: nextcord.Interaction,
        유저: nextcord.Member,
        포인트: int
    ):
        user_id = str(유저.id)
        user_data = self.get_user_data(user_id)

        user_data["points"] += 포인트
        self.save_data()

        action = "지급" if 포인트 > 0 else "차감"
        embed = nextcord.Embed(
            title=f"✅ 포인트 {action} 완료",
            description=f"{유저.mention}님에게 {abs(포인트)}P를 {action}했습니다.",
            color=nextcord.Color.green()
        )
        embed.add_field(name="현재 포인트", value=f"{user_data['points']}P", inline=True)

        await ctx.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Attendance(bot))
