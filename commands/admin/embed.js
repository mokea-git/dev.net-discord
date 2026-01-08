import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('임베드')
  .setDescription('커스텀 임베드를 생성합니다')
  .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
  .addStringOption((option) => option.setName('제목').setDescription('임베드 제목').setRequired(true))
  .addStringOption((option) => option.setName('내용').setDescription('임베드 내용').setRequired(true))
  .addStringOption((option) =>
    option
      .setName('색상')
      .setDescription('색상 선택')
      .setRequired(true)
      .addChoices(
        { name: '빨강', value: 'red' },
        { name: '파랑', value: 'blue' },
        { name: '초록', value: 'green' },
        { name: '노랑', value: 'yellow' },
        { name: '보라', value: 'purple' }
      )
  );

export async function execute(interaction) {
  const 제목 = interaction.options.getString('제목');
  const 내용 = interaction.options.getString('내용');
  const 색상 = interaction.options.getString('색상');

  const colors = {
    red: 0xff0000,
    blue: 0x0000ff,
    green: 0x00ff00,
    yellow: 0xffd700,
    purple: 0x800080,
  };

  const embed = new EmbedBuilder()
    .setTitle(제목)
    .setDescription(내용)
    .setColor(colors[색상] || colors.blue);

  await interaction.reply({ embeds: [embed] });
}
