import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { PUNISH_LOG_CHANNEL_ID } from '../../config.js';

export const data = new SlashCommandBuilder()
  .setName('추방')
  .setDescription('유저를 추방합니다')
  .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
  .addUserOption((option) => option.setName('유저').setDescription('추방할 유저').setRequired(true))
  .addStringOption((option) =>
    option.setName('사유').setDescription('추방 사유').setRequired(false)
  );

export async function execute(interaction) {
  const user = interaction.options.getUser('유저');
  const 사유 = interaction.options.getString('사유') || '사유 없음';
  const member = await interaction.guild.members.fetch(user.id);

  if (member.roles.highest.position >= interaction.member.roles.highest.position) {
    await interaction.reply({
      content: '자신보다 높거나 같은 역할의 유저는 추방할 수 없습니다.',
      ephemeral: true,
    });
    return;
  }

  // DM 전송 시도
  try {
    const dmEmbed = new EmbedBuilder()
      .setTitle('👢 추방되었습니다')
      .setDescription(`**${interaction.guild.name}** 서버에서 추방되었습니다.`)
      .setColor(0xffa500)
      .addFields({ name: '사유', value: 사유, inline: false });

    await member.send({ embeds: [dmEmbed] });
  } catch (error) {
    // DM 전송 실패 무시
  }

  await member.kick(사유);

  const embed = new EmbedBuilder()
    .setTitle('👢 추방 완료')
    .setColor(0xffa500)
    .addFields(
      { name: '추방된 유저', value: `${user.username}#${user.discriminator}`, inline: true },
      { name: '사유', value: 사유, inline: true },
      { name: '처리자', value: interaction.user.toString(), inline: true }
    );

  await interaction.reply({ embeds: [embed] });

  // 로그 채널에 기록
  const logChannel = interaction.guild.channels.cache.get(PUNISH_LOG_CHANNEL_ID);
  if (logChannel) {
    const logEmbed = new EmbedBuilder()
      .setTitle('👢 추방')
      .setDescription(`**${user.username}**님이 추방되었습니다.`)
      .setColor(0xffa500)
      .setTimestamp()
      .addFields(
        { name: '대상', value: `${user.username}#${user.discriminator}`, inline: true },
        { name: '처리자', value: interaction.user.toString(), inline: true },
        { name: '사유', value: 사유, inline: false }
      );

    await logChannel.send({ embeds: [logEmbed] });
  }
}
