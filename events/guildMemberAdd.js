import { Events, EmbedBuilder } from 'discord.js';
import { WELCOME_CHANNEL_ID } from '../config.js';

export const name = Events.GuildMemberAdd;

export async function execute(member) {
  const channel = member.guild.channels.cache.get(WELCOME_CHANNEL_ID);

  if (!channel) return;

  const embed = new EmbedBuilder()
    .setTitle('👋 환영합니다!')
    .setDescription(`${member}님이 서버에 입장했습니다!`)
    .setColor(0x00ff00)
    .setThumbnail(member.user.displayAvatarURL())
    .addFields({ name: '멤버 수', value: `${member.guild.memberCount}명`, inline: true });

  await channel.send({ embeds: [embed] });
}
