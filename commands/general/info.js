import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export const data = new SlashCommandBuilder().setName('정보').setDescription('봇 정보를 확인합니다');

export async function execute(interaction) {
  const embed = new EmbedBuilder()
    .setTitle('DEV.NET')
    .setDescription('서버 관리를 위한 다목적 봇입니다.')
    .setColor(0x5865f2)
    .setThumbnail(interaction.client.user.displayAvatarURL())
    .addFields(
      { name: '개발자', value: 'mokea', inline: true },
      { name: '버전', value: '2.0.0 (Node.js)', inline: true },
      { name: '링크', value: '[웹사이트](https://mokea.dev)', inline: false }
    );

  await interaction.reply({ embeds: [embed] });
}
