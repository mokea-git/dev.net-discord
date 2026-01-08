import { Events, EmbedBuilder } from 'discord.js';
import { EXTENDED_LOG_CHANNEL_ID } from '../config.js';

export const name = Events.VoiceStateUpdate;

export async function execute(oldState, newState) {
  const logChannel = oldState.guild.channels.cache.get(EXTENDED_LOG_CHANNEL_ID);
  if (!logChannel) return;

  const member = newState.member;

  // 음성 채널 입장
  if (!oldState.channel && newState.channel) {
    const embed = new EmbedBuilder()
      .setTitle('🔊 음성 채널 입장')
      .setDescription(`${member}님이 ${newState.channel}에 입장했습니다.`)
      .setColor(0x00ff00);

    await logChannel.send({ embeds: [embed] });
  }
  // 음성 채널 퇴장
  else if (oldState.channel && !newState.channel) {
    const embed = new EmbedBuilder()
      .setTitle('🔇 음성 채널 퇴장')
      .setDescription(`${member}님이 ${oldState.channel}에서 퇴장했습니다.`)
      .setColor(0xff0000);

    await logChannel.send({ embeds: [embed] });
  }
  // 음성 채널 이동
  else if (oldState.channel && newState.channel && oldState.channel.id !== newState.channel.id) {
    const embed = new EmbedBuilder()
      .setTitle('🔀 음성 채널 이동')
      .setDescription(`${member}님이 ${oldState.channel}에서 ${newState.channel}로 이동했습니다.`)
      .setColor(0x0000ff);

    await logChannel.send({ embeds: [embed] });
  }
}
