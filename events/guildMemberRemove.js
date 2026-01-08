import { Events, EmbedBuilder } from 'discord.js';
import { WELCOME_CHANNEL_ID } from '../config.js';

export const name = Events.GuildMemberRemove;

export async function execute(member) {
  const channel = member.guild.channels.cache.get(WELCOME_CHANNEL_ID);

  if (!channel) return;

  const embed = new EmbedBuilder()
    .setTitle('👋 안녕히 가세요')
    .setDescription(`**${member.user.username}**님이 서버를 떠났습니다.`)
    .setColor(0xff0000);

  await channel.send({ embeds: [embed] });
}
