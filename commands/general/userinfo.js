import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('유저정보')
  .setDescription('유저 정보를 조회합니다')
  .addUserOption((option) => option.setName('유저').setDescription('조회할 유저').setRequired(false));

export async function execute(interaction) {
  const user = interaction.options.getUser('유저') || interaction.user;
  const member = await interaction.guild.members.fetch(user.id);

  const roles = member.roles.cache.filter((role) => role.name !== '@everyone').map((role) => role.toString());

  const embed = new EmbedBuilder()
    .setTitle(`👤 ${user.username} 정보`)
    .setColor(member.displayColor)
    .setThumbnail(user.displayAvatarURL())
    .addFields(
      { name: 'ID', value: user.id, inline: true },
      { name: '닉네임', value: member.displayName, inline: true },
      {
        name: '계정 생성일',
        value: user.createdAt.toLocaleDateString('ko-KR'),
        inline: true,
      },
      {
        name: '서버 가입일',
        value: member.joinedAt.toLocaleDateString('ko-KR'),
        inline: true,
      },
      {
        name: `역할 (${roles.length}개)`,
        value: roles.join(' ') || '없음',
        inline: false,
      }
    );

  await interaction.reply({ embeds: [embed] });
}
