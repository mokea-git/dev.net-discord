import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export const data = new SlashCommandBuilder().setName('서버정보').setDescription('서버 정보를 조회합니다');

export async function execute(interaction) {
  const guild = interaction.guild;

  const embed = new EmbedBuilder()
    .setTitle(`🏠 ${guild.name}`)
    .setColor(0x00ff00)
    .addFields(
      { name: '서버 ID', value: guild.id, inline: true },
      { name: '서버 주인', value: `<@${guild.ownerId}>`, inline: true },
      {
        name: '생성일',
        value: guild.createdAt.toLocaleDateString('ko-KR'),
        inline: true,
      },
      { name: '멤버 수', value: `${guild.memberCount}명`, inline: true },
      { name: '채널 수', value: `${guild.channels.cache.size}개`, inline: true },
      { name: '역할 수', value: `${guild.roles.cache.size}개`, inline: true }
    );

  if (guild.iconURL()) {
    embed.setThumbnail(guild.iconURL());
  }

  await interaction.reply({ embeds: [embed] });
}
