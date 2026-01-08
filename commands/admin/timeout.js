import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { PUNISH_LOG_CHANNEL_ID } from '../../config.js';

export const data = new SlashCommandBuilder()
  .setName('타임아웃')
  .setDescription('유저를 타임아웃합니다')
  .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
  .addUserOption((option) => option.setName('유저').setDescription('타임아웃할 유저').setRequired(true))
  .addIntegerOption((option) =>
    option
      .setName('시간')
      .setDescription('타임아웃 시간(분)')
      .setRequired(true)
      .setMinValue(1)
      .setMaxValue(40320)
  )
  .addStringOption((option) => option.setName('사유').setDescription('타임아웃 사유').setRequired(false));

export async function execute(interaction) {
  const user = interaction.options.getUser('유저');
  const 시간 = interaction.options.getInteger('시간');
  const 사유 = interaction.options.getString('사유') || '사유 없음';
  const member = await interaction.guild.members.fetch(user.id);

  if (member.roles.highest.position >= interaction.member.roles.highest.position) {
    await interaction.reply({
      content: '자신보다 높거나 같은 역할의 유저는 타임아웃할 수 없습니다.',
      ephemeral: true,
    });
    return;
  }

  await interaction.deferReply();

  // DM 전송 시도
  try {
    const dmEmbed = new EmbedBuilder()
      .setTitle('🔇 타임아웃되었습니다')
      .setDescription(`**${interaction.guild.name}** 서버에서 타임아웃되었습니다.`)
      .setColor(0x808080)
      .addFields(
        { name: '시간', value: `${시간}분`, inline: true },
        { name: '사유', value: 사유, inline: false }
      );

    await member.send({ embeds: [dmEmbed] });
  } catch (error) {
    // DM 전송 실패 무시
  }

  await member.timeout(시간 * 60 * 1000, 사유);

  const embed = new EmbedBuilder()
    .setTitle('🔇 타임아웃 완료')
    .setColor(0x808080)
    .addFields(
      { name: '타임아웃된 유저', value: member.toString(), inline: true },
      { name: '시간', value: `${시간}분`, inline: true },
      { name: '사유', value: 사유, inline: false }
    )
    .setFooter({ text: `처리자: ${interaction.user.username}` });

  await interaction.followUp({ embeds: [embed] });

  // 로그 채널에 기록
  const logChannel = interaction.guild.channels.cache.get(PUNISH_LOG_CHANNEL_ID);
  if (logChannel) {
    const logEmbed = new EmbedBuilder()
      .setTitle('🔇 타임아웃')
      .setDescription(`**${user.username}**님이 타임아웃되었습니다.`)
      .setColor(0x808080)
      .setTimestamp()
      .addFields(
        { name: '대상', value: member.toString(), inline: true },
        { name: '시간', value: `${시간}분`, inline: true },
        { name: '처리자', value: interaction.user.toString(), inline: true },
        { name: '사유', value: 사유, inline: false }
      );

    await logChannel.send({ embeds: [logEmbed] });
  }
}
