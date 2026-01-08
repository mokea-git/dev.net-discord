import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('아바타')
  .setDescription('유저의 프로필 사진을 확인합니다')
  .addUserOption((option) => option.setName('유저').setDescription('확인할 유저').setRequired(false));

export async function execute(interaction) {
  const user = interaction.options.getUser('유저') || interaction.user;
  const member = await interaction.guild.members.fetch(user.id);

  const embed = new EmbedBuilder()
    .setTitle(`🖼️ ${user.username}의 아바타`)
    .setColor(member.displayColor)
    .setImage(user.displayAvatarURL({ size: 1024 }));

  await interaction.reply({ embeds: [embed] });
}
