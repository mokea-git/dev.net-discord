import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View, Modal, TextInput
import asyncio
import io

from config import GUILD_ID, ADMIN_ROLE_ID, TICKET_CATEGORY_ID, LOG_CHANNEL_ID


# 신고 티켓 번호 (메모리 저장, 봇 재시작 시 초기화)
report_ticket_number = 0


class ReportModal(Modal):
    def __init__(self):
        super().__init__(title="신고하기")

        self.reported_user = TextInput(
            label="신고 대상",
            placeholder="신고할 유저의 닉네임 또는 ID",
            required=True,
            max_length=100
        )
        self.add_item(self.reported_user)

        self.reason = TextInput(
            label="신고 사유",
            placeholder="신고 사유를 자세히 작성해주세요",
            style=nextcord.TextInputStyle.paragraph,
            required=True,
            max_length=1000
        )
        self.add_item(self.reason)

    async def callback(self, interaction: nextcord.Interaction):
        global report_ticket_number
        report_ticket_number += 1

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        admin_role = guild.get_role(ADMIN_ROLE_ID)
        log_channel = guild.get_channel(LOG_CHANNEL_ID)

        if category is None or admin_role is None:
            await interaction.response.send_message(
                "설정이 올바르지 않습니다.",
                ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(view_channel=False),
            interaction.user: nextcord.PermissionOverwrite(view_channel=True, send_messages=True),
            admin_role: nextcord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        channel = await guild.create_text_channel(
            name=f"신고-{report_ticket_number:03d}",
            category=category,
            overwrites=overwrites
        )

        close_button = Button(label="🔒 신고 닫기", style=nextcord.ButtonStyle.red)

        async def close_report(interaction2: nextcord.Interaction):
            if admin_role not in interaction2.user.roles:
                await interaction2.response.send_message(
                    "관리자만 닫을 수 있습니다.",
                    ephemeral=True
                )
                return

            await interaction2.response.send_message("5초 후 닫힙니다.")

            messages = []
            async for msg in channel.history(limit=None, oldest_first=True):
                messages.append(f"[{msg.author}] {msg.content}")

            file_content = "\n".join(messages)
            file = nextcord.File(
                io.BytesIO(file_content.encode("utf-8")),
                filename=f"{channel.name}.txt"
            )

            if log_channel:
                await log_channel.send(
                    f"🚨 신고 종료\n"
                    f"신고자: {interaction.user}\n"
                    f"채널: {channel.name}",
                    file=file
                )

            await asyncio.sleep(5)
            await channel.delete()

        close_button.callback = close_report
        close_view = View(timeout=None)
        close_view.add_item(close_button)

        embed = nextcord.Embed(
            title="🚨 신고 접수",
            color=nextcord.Color.red()
        )
        embed.add_field(name="신고자", value=interaction.user.mention, inline=True)
        embed.add_field(name="신고 대상", value=self.reported_user.value, inline=True)
        embed.add_field(name="신고 사유", value=self.reason.value, inline=False)

        await channel.send(
            f"{admin_role.mention} 새로운 신고가 접수되었습니다!",
            embed=embed,
            view=close_view
        )

        if log_channel:
            await log_channel.send(
                f"🚨 신고 생성\n"
                f"신고자: {interaction.user}\n"
                f"신고 대상: {self.reported_user.value}\n"
                f"채널: {channel.mention}"
            )

        await interaction.response.send_message(
            f"신고가 접수되었습니다 👉 {channel.mention}",
            ephemeral=True
        )


class TicketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ─────────────────────────
    # 티켓 시스템
    # ─────────────────────────
    @nextcord.slash_command(
        name="ticket",
        description="티켓 생성 버튼을 보냅니다",
        default_member_permissions=nextcord.Permissions(administrator=True)
    )
    async def ticket(self, ctx: nextcord.Interaction):

        create_button = Button(label="🎫 티켓 만들기", style=nextcord.ButtonStyle.green)

        async def create_ticket(interaction: nextcord.Interaction):
            guild = interaction.guild
            category = guild.get_channel(TICKET_CATEGORY_ID)
            admin_role = guild.get_role(ADMIN_ROLE_ID)
            log_channel = guild.get_channel(LOG_CHANNEL_ID)

            if category is None or admin_role is None:
                await interaction.response.send_message(
                    "티켓 설정이 올바르지 않습니다.",
                    ephemeral=True
                )
                return

            for ch in category.text_channels:
                if ch.name == f"ticket-{interaction.user.id}":
                    await interaction.response.send_message(
                        "이미 열려 있는 티켓이 있습니다.",
                        ephemeral=True
                    )
                    return

            overwrites = {
                guild.default_role: nextcord.PermissionOverwrite(view_channel=False),
                interaction.user: nextcord.PermissionOverwrite(view_channel=True, send_messages=True),
                admin_role: nextcord.PermissionOverwrite(view_channel=True, send_messages=True),
            }

            channel = await guild.create_text_channel(
                name=f"ticket-{interaction.user.id}",
                category=category,
                overwrites=overwrites
            )

            close_button = Button(label="🔒 티켓 닫기", style=nextcord.ButtonStyle.red)

            async def close_ticket(interaction2: nextcord.Interaction):
                if admin_role not in interaction2.user.roles:
                    await interaction2.response.send_message(
                        "관리자만 티켓을 닫을 수 있습니다.",
                        ephemeral=True
                    )
                    return

                await interaction2.response.send_message(
                    "티켓이 5초 후 닫힙니다.",
                    ephemeral=True
                )

                messages = []
                async for msg in channel.history(limit=None, oldest_first=True):
                    messages.append(f"[{msg.author}] {msg.content}")

                file_content = "\n".join(messages)
                file = nextcord.File(
                    io.BytesIO(file_content.encode("utf-8")),
                    filename=f"{channel.name}.txt"
                )

                if log_channel:
                    await log_channel.send(
                        f"🧾 티켓 종료\n유저: {interaction.user}",
                        file=file
                    )

                await asyncio.sleep(5)
                await channel.delete()

            close_button.callback = close_ticket

            close_view = View(timeout=None)
            close_view.add_item(close_button)

            await channel.send(
                f"{interaction.user.mention} 님의 티켓입니다.\n"
                f"{admin_role.mention}\n"
                "문의 내용을 적어주세요.",
                view=close_view
            )

            if log_channel:
                await log_channel.send(
                    f"🧾 티켓 생성\n유저: {interaction.user}\n채널: {channel.name}"
                )

            await interaction.response.send_message(
                f"티켓이 생성되었습니다 👉 {channel.mention}",
                ephemeral=True
            )

        create_button.callback = create_ticket
        view = View(timeout=None)
        view.add_item(create_button)

        await ctx.response.send_message(
            "아래 버튼을 눌러 티켓을 생성하세요.",
            view=view
        )

    # ─────────────────────────
    # /신고 명령어 (관리자 전용)
    # ─────────────────────────
    @nextcord.slash_command(
        name="신고",
        description="신고 버튼을 생성합니다",
        default_member_permissions=nextcord.Permissions(administrator=True),
        guild_ids=[GUILD_ID]
    )
    async def report_setup(self, ctx: nextcord.Interaction):

        report_button = Button(label="🚨 신고하기", style=nextcord.ButtonStyle.red)

        async def open_report_modal(interaction: nextcord.Interaction):
            await interaction.response.send_modal(ReportModal())

        report_button.callback = open_report_modal
        view = View(timeout=None)
        view.add_item(report_button)

        embed = nextcord.Embed(
            title="🚨 신고 시스템",
            description="규칙 위반자를 신고하려면 아래 버튼을 눌러주세요.",
            color=nextcord.Color.red()
        )

        await ctx.response.send_message(embed=embed, view=view)


def setup(bot):
    bot.add_cog(TicketCommands(bot))
