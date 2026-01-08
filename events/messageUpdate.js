import { Events, EmbedBuilder } from 'discord.js';
import { EXTENDED_LOG_CHANNEL_ID } from '../config.js';

export const name = Events.MessageUpdate;

export async function execute(oldMessage, newMessage) {
  // 봇 메시지 무시
  if (oldMessage.author?.bot) return;

  // 내용이 같으면 무시 (임베드 업데이트 등)
  if (oldMessage.content === newMessage.content) return;

  const logChannel = oldMessage.guild.channels.cache.get(EXTENDED_LOG_CHANNEL_ID);
  if (!logChannel) return;

  const embed = new EmbedBuilder()
    .setTitle('✏️ 메시지 수정됨')
    .setColor(0xffa500)
    .setTimestamp(newMessage.editedAt)
    .addFields(
      { name: '작성자', value: oldMessage.author.toString(), inline: true },
      { name: '채널', value: oldMessage.channel.toString(), inline: true },
      {
        name: '수정 전',
        value: oldMessage.content?.slice(0, 1024) || '*내용 없음*',
        inline: false,
      },
      {
        name: '수정 후',
        value: newMessage.content?.slice(0, 1024) || '*내용 없음*',
        inline: false,
      },
      { name: '메시지 링크', value: `[바로가기](${newMessage.url})`, inline: false }
    );

  await logChannel.send({ embeds: [embed] });
}
