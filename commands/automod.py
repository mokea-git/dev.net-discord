import nextcord
from nextcord.ext import commands
from nextcord import SlashOption
import re
from datetime import timedelta

from config import GUILD_ID, ADMIN_ROLE_ID

# 욕설 목록 (예시)
PROFANITY_LIST = [
    "시발", "씨발", "병신", "좆", "지랄", "개새", "새끼",
    "ㅅㅂ", "ㅂㅅ", "ㅈㄹ", "fuck", "shit", "bitch"
]

# 스팸 감지 설정
SPAM_MESSAGE_COUNT = 5  # 메시지 개수
SPAM_TIME_WINDOW = 5    # 초 단위
SPAM_PUNISHMENT = "timeout"  # timeout 또는 kick


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_message_times = {}  # {user_id: [timestamp1, timestamp2, ...]}
        self.automod_enabled = True
        self.profanity_filter_enabled = True
        self.spam_filter_enabled = True

    # ─────────────────────────
    # 메시지 감지
    # ─────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        # 봇 메시지 무시
        if message.author.bot:
            return

        # 관리자 무시
        if any(role.id == ADMIN_ROLE_ID for role in message.author.roles):
            return

        # 자동 조정 비활성화 시 무시
        if not self.automod_enabled:
            return

        # 욕설 필터링
        if self.profanity_filter_enabled:
            if await self.check_profanity(message):
                return

        # 스팸 필터링
        if self.spam_filter_enabled:
            await self.check_spam(message)

    async def check_profanity(self, message: nextcord.Message):
        """욕설 감지 및 처리"""
        content_lower = message.content.lower()

        for word in PROFANITY_LIST:
            if word in content_lower:
                # 메시지 삭제
                await message.delete()

                # 경고 메시지
                warning = await message.channel.send(
                    f"⚠️ {message.author.mention} 욕설은 사용할 수 없습니다."
                )

                # 3초 후 경고 메시지 삭제
                await warning.delete(delay=3)

                # 타임아웃 (1분)
                try:
                    await message.author.timeout(timedelta(minutes=1), reason="욕설 사용")
                except:
                    pass

                return True

        return False

    async def check_spam(self, message: nextcord.Message):
        """스팸 감지 및 처리"""
        import time

        user_id = message.author.id
        current_time = time.time()

        # 유저의 메시지 타임스탬프 가져오기
        if user_id not in self.user_message_times:
            self.user_message_times[user_id] = []

        # 현재 시간 추가
        self.user_message_times[user_id].append(current_time)

        # 오래된 타임스탬프 제거 (시간 윈도우 밖)
        self.user_message_times[user_id] = [
            t for t in self.user_message_times[user_id]
            if current_time - t <= SPAM_TIME_WINDOW
        ]

        # 스팸 감지
        if len(self.user_message_times[user_id]) >= SPAM_MESSAGE_COUNT:
            # 메시지 삭제 시도
            try:
                async for msg in message.channel.history(limit=SPAM_MESSAGE_COUNT):
                    if msg.author.id == user_id:
                        await msg.delete()
            except:
                pass

            # 경고 메시지
            warning = await message.channel.send(
                f"⚠️ {message.author.mention} 스팸 감지! 메시지를 천천히 보내주세요."
            )
            await warning.delete(delay=5)

            # 처벌
            if SPAM_PUNISHMENT == "timeout":
                try:
                    await message.author.timeout(timedelta(minutes=5), reason="스팸")
                except:
                    pass
            elif SPAM_PUNISHMENT == "kick":
                try:
                    await message.author.kick(reason="스팸")
                except:
                    pass

            # 타임스탬프 초기화
            self.user_message_times[user_id] = []

    # ─────────────────────────
    # 자동 조정 설정
    # ─────────────────────────
    @nextcord.slash_command(
        name="자동조정",
        description="자동 조정 설정을 관리합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def automod_settings(
        self,
        ctx: nextcord.Interaction,
        기능: str = SlashOption(
            description="설정할 기능",
            choices=["전체", "욕설필터", "스팸필터"]
        ),
        상태: str = SlashOption(
            description="활성화/비활성화",
            choices=["활성화", "비활성화"]
        )
    ):
        enabled = (상태 == "활성화")

        if 기능 == "전체":
            self.automod_enabled = enabled
            self.profanity_filter_enabled = enabled
            self.spam_filter_enabled = enabled
            msg = f"자동 조정 전체 기능이 **{상태}**되었습니다."
        elif 기능 == "욕설필터":
            self.profanity_filter_enabled = enabled
            msg = f"욕설 필터가 **{상태}**되었습니다."
        elif 기능 == "스팸필터":
            self.spam_filter_enabled = enabled
            msg = f"스팸 필터가 **{상태}**되었습니다."

        embed = nextcord.Embed(
            title="⚙️ 자동 조정 설정",
            description=msg,
            color=nextcord.Color.green() if enabled else nextcord.Color.red()
        )
        await ctx.response.send_message(embed=embed)

    # ─────────────────────────
    # 욕설 목록 관리
    # ─────────────────────────
    @nextcord.slash_command(
        name="욕설목록",
        description="욕설 필터 목록을 관리합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def profanity_list(
        self,
        ctx: nextcord.Interaction,
        행동: str = SlashOption(
            description="수행할 행동",
            choices=["보기", "추가", "제거"]
        ),
        단어: str = SlashOption(description="추가/제거할 단어", required=False)
    ):
        if 행동 == "보기":
            embed = nextcord.Embed(
                title="📋 욕설 필터 목록",
                description=", ".join(f"`{word}`" for word in PROFANITY_LIST),
                color=nextcord.Color.blue()
            )
            await ctx.response.send_message(embed=embed, ephemeral=True)

        elif 행동 == "추가":
            if not 단어:
                await ctx.response.send_message("단어를 입력해주세요.", ephemeral=True)
                return

            if 단어 not in PROFANITY_LIST:
                PROFANITY_LIST.append(단어.lower())
                await ctx.response.send_message(f"✅ `{단어}`를 욕설 목록에 추가했습니다.", ephemeral=True)
            else:
                await ctx.response.send_message(f"⚠️ `{단어}`는 이미 목록에 있습니다.", ephemeral=True)

        elif 행동 == "제거":
            if not 단어:
                await ctx.response.send_message("단어를 입력해주세요.", ephemeral=True)
                return

            if 단어.lower() in PROFANITY_LIST:
                PROFANITY_LIST.remove(단어.lower())
                await ctx.response.send_message(f"✅ `{단어}`를 욕설 목록에서 제거했습니다.", ephemeral=True)
            else:
                await ctx.response.send_message(f"⚠️ `{단어}`는 목록에 없습니다.", ephemeral=True)


def setup(bot):
    bot.add_cog(AutoMod(bot))
