import { SlashCommandBuilder } from 'discord.js';

export const data = new SlashCommandBuilder().setName('핑').setDescription('봇의 응답 속도를 확인합니다');

export async function execute(interaction) {
  const latency = Math.round(interaction.client.ws.ping);
  await interaction.reply(`🏓 퐁! \`${latency}ms\``);
}
