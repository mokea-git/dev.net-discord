import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { ANNOUNCE_CHANNEL_ID } from '../../config.js';

export const data = new SlashCommandBuilder()
  .setName('공지')
  .setDescription('공지를 작성합니다')
  .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
  .addStringOption((option) => option.setName('제목').setDescription('공지 제목').setRequired(true))
  .addStringOption((option) => option.setName('내용').setDescription('공지 내용').setRequired(true));

export async function execute(interaction) {
  const 제목 = interaction.options.getString('제목');
  const 내용 = interaction.options.getString('내용');

  const channel = interaction.guild.channels.cache.get(ANNOUNCE_CHANNEL_ID);

  if (!channel) {
    await interaction.reply({ content: '공지 채널을 찾을 수 없습니다.', ephemeral: true });
    return;
  }

  const embed = new EmbedBuilder()
    .setTitle(`📢 ${제목}`)
    .setDescription(내용)
    .setColor(0x0000ff)
    .setTimestamp()
    .setFooter({ text: `작성자: ${interaction.user.username}` });

  await channel.send({ embeds: [embed] });
  await interaction.reply({
    content: `공지가 전송되었습니다! 👉 ${channel}`,
    ephemeral: true,
  });
}
