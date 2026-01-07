import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import json
from datetime import datetime
import os

from config import GUILD_ID


class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.backup_dir = "backups"

        # backups 디렉토리 생성
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    # ─────────────────────────
    # 서버 백업
    # ─────────────────────────
    @nextcord.slash_command(
        name="백업",
        description="서버 설정과 역할을 백업합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def backup(self, ctx: nextcord.Interaction):
        await ctx.response.defer(ephemeral=True)

        guild = ctx.guild
        backup_data = {
            "backup_date": datetime.now().isoformat(),
            "guild_id": guild.id,
            "guild_name": guild.name,
            "roles": [],
            "channels": [],
            "categories": []
        }

        # 역할 백업
        for role in guild.roles:
            if role.name != "@everyone":
                role_data = {
                    "name": role.name,
                    "color": str(role.color),
                    "permissions": role.permissions.value,
                    "hoist": role.hoist,
                    "mentionable": role.mentionable,
                    "position": role.position
                }
                backup_data["roles"].append(role_data)

        # 카테고리 백업
        for category in guild.categories:
            category_data = {
                "name": category.name,
                "position": category.position,
                "nsfw": category.nsfw
            }
            backup_data["categories"].append(category_data)

        # 채널 백업
        for channel in guild.channels:
            if isinstance(channel, nextcord.TextChannel):
                channel_data = {
                    "type": "text",
                    "name": channel.name,
                    "category": channel.category.name if channel.category else None,
                    "position": channel.position,
                    "topic": channel.topic,
                    "slowmode_delay": channel.slowmode_delay,
                    "nsfw": channel.nsfw
                }
                backup_data["channels"].append(channel_data)
            elif isinstance(channel, nextcord.VoiceChannel):
                channel_data = {
                    "type": "voice",
                    "name": channel.name,
                    "category": channel.category.name if channel.category else None,
                    "position": channel.position,
                    "bitrate": channel.bitrate,
                    "user_limit": channel.user_limit
                }
                backup_data["channels"].append(channel_data)

        # JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.backup_dir}/backup_{guild.id}_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        embed = nextcord.Embed(
            title="✅ 백업 완료",
            description=f"서버 설정이 백업되었습니다.\n\n"
                        f"**역할:** {len(backup_data['roles'])}개\n"
                        f"**카테고리:** {len(backup_data['categories'])}개\n"
                        f"**채널:** {len(backup_data['channels'])}개\n"
                        f"**파일:** `{filename}`",
            color=nextcord.Color.green()
        )
        embed.set_footer(text=f"백업 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        await ctx.followup.send(embed=embed, ephemeral=True)

    # ─────────────────────────
    # 백업 목록
    # ─────────────────────────
    @nextcord.slash_command(
        name="백업목록",
        description="저장된 백업 목록을 확인합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def backup_list(self, ctx: nextcord.Interaction):
        backups = [f for f in os.listdir(self.backup_dir) if f.endswith('.json')]

        if not backups:
            await ctx.response.send_message("저장된 백업이 없습니다.", ephemeral=True)
            return

        # 최신순 정렬
        backups.sort(reverse=True)

        # 최대 10개만 표시
        backups = backups[:10]

        embed = nextcord.Embed(
            title="💾 백업 목록",
            description="최근 백업 파일 목록입니다.",
            color=nextcord.Color.blue()
        )

        for backup in backups:
            # 파일명에서 날짜 추출
            parts = backup.replace("backup_", "").replace(".json", "").split("_")
            if len(parts) >= 3:
                date_str = parts[1]
                time_str = parts[2]
                formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]} {time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"
                embed.add_field(
                    name=formatted_date,
                    value=f"`{backup}`",
                    inline=False
                )

        await ctx.response.send_message(embed=embed, ephemeral=True)

    # ─────────────────────────
    # 백업 복원
    # ─────────────────────────
    @nextcord.slash_command(
        name="백업복원",
        description="백업 파일에서 서버 설정을 복원합니다 (주의: 기존 설정이 변경됩니다)",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def restore(
        self,
        ctx: nextcord.Interaction,
        파일명: str = SlashOption(description="복원할 백업 파일명")
    ):
        await ctx.response.defer(ephemeral=True)

        filepath = f"{self.backup_dir}/{파일명}"

        if not os.path.exists(filepath):
            await ctx.followup.send("❌ 백업 파일을 찾을 수 없습니다.", ephemeral=True)
            return

        # 백업 파일 읽기
        with open(filepath, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)

        guild = ctx.guild
        restored = {
            "roles": 0,
            "categories": 0,
            "channels": 0
        }

        # 역할 복원
        for role_data in backup_data["roles"]:
            try:
                # 이미 존재하는 역할인지 확인
                existing_role = nextcord.utils.get(guild.roles, name=role_data["name"])
                if not existing_role:
                    await guild.create_role(
                        name=role_data["name"],
                        color=nextcord.Color(int(role_data["color"].replace("#", ""), 16)),
                        permissions=nextcord.Permissions(role_data["permissions"]),
                        hoist=role_data["hoist"],
                        mentionable=role_data["mentionable"]
                    )
                    restored["roles"] += 1
            except Exception as e:
                print(f"역할 복원 실패: {role_data['name']} - {e}")

        # 카테고리 복원
        for category_data in backup_data["categories"]:
            try:
                existing_category = nextcord.utils.get(guild.categories, name=category_data["name"])
                if not existing_category:
                    await guild.create_category(
                        name=category_data["name"],
                        position=category_data["position"]
                    )
                    restored["categories"] += 1
            except Exception as e:
                print(f"카테고리 복원 실패: {category_data['name']} - {e}")

        # 채널 복원
        for channel_data in backup_data["channels"]:
            try:
                if channel_data["type"] == "text":
                    existing_channel = nextcord.utils.get(guild.text_channels, name=channel_data["name"])
                    if not existing_channel:
                        category = nextcord.utils.get(guild.categories, name=channel_data["category"]) if channel_data["category"] else None
                        await guild.create_text_channel(
                            name=channel_data["name"],
                            category=category,
                            topic=channel_data["topic"],
                            slowmode_delay=channel_data["slowmode_delay"],
                            nsfw=channel_data["nsfw"]
                        )
                        restored["channels"] += 1
                elif channel_data["type"] == "voice":
                    existing_channel = nextcord.utils.get(guild.voice_channels, name=channel_data["name"])
                    if not existing_channel:
                        category = nextcord.utils.get(guild.categories, name=channel_data["category"]) if channel_data["category"] else None
                        await guild.create_voice_channel(
                            name=channel_data["name"],
                            category=category,
                            bitrate=channel_data["bitrate"],
                            user_limit=channel_data["user_limit"]
                        )
                        restored["channels"] += 1
            except Exception as e:
                print(f"채널 복원 실패: {channel_data['name']} - {e}")

        embed = nextcord.Embed(
            title="✅ 백업 복원 완료",
            description=f"백업 파일에서 서버 설정을 복원했습니다.\n\n"
                        f"**복원된 역할:** {restored['roles']}개\n"
                        f"**복원된 카테고리:** {restored['categories']}개\n"
                        f"**복원된 채널:** {restored['channels']}개",
            color=nextcord.Color.green()
        )
        embed.set_footer(text="이미 존재하는 항목은 건너뛰었습니다.")

        await ctx.followup.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Backup(bot))
