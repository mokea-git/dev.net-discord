import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { PUNISH_LOG_CHANNEL_ID } from '../../config.js';

export const data = new SlashCommandBuilder()
  .setName('언밴')
  .setDescription('유저의 밴을 해제합니다')
  .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
  .addStringOption((option) => option.setName('유저id').setDescription('언밴할 유저의 ID').setRequired(true));

export async function execute(interaction) {
  const 유저id = interaction.options.getString('유저id');

  try {
    const user = await interaction.client.users.fetch(유저id);
    await interaction.guild.members.unban(user);

    const embed = new EmbedBuilder()
      .setTitle('✅ 언밴 완료')
      .setColor(0x00ff00)
      .addFields(
        { name: '언밴된 유저', value: `${user.username}#${user.discriminator}`, inline: true },
        { name: '처리자', value: interaction.user.toString(), inline: true }
      );

    await interaction.reply({ embeds: [embed] });

    // 로그 채널에 기록
    const logChannel = interaction.guild.channels.cache.get(PUNISH_LOG_CHANNEL_ID);
    if (logChannel) {
      const logEmbed = new EmbedBuilder()
        .setTitle('✅ 언밴')
        .setDescription(`**${user.username}**님의 밴이 해제되었습니다.`)
        .setColor(0x00ff00)
        .setTimestamp()
        .addFields(
          { name: '대상', value: `${user.username}#${user.discriminator}`, inline: true },
          { name: '처리자', value: interaction.user.toString(), inline: true }
        );

      await logChannel.send({ embeds: [logEmbed] });
    }
  } catch (error) {
    if (error.code === 10013) {
      await interaction.reply({ content: '해당 유저를 찾을 수 없거나 밴 목록에 없습니다.', ephemeral: true });
    } else {
      await interaction.reply({ content: `오류가 발생했습니다: ${error.message}`, ephemeral: true });
    }
  }
}
