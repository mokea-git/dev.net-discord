import { Events, EmbedBuilder } from 'discord.js';
import { EXTENDED_LOG_CHANNEL_ID } from '../config.js';

export const name = Events.MessageDelete;

export async function execute(message) {
  // 봇 메시지 무시
  if (message.author?.bot) return;

  const logChannel = message.guild.channels.cache.get(EXTENDED_LOG_CHANNEL_ID);
  if (!logChannel) return;

  const embed = new EmbedBuilder()
    .setTitle('🗑️ 메시지 삭제됨')
    .setColor(0xff0000)
    .setTimestamp(message.createdAt)
    .addFields(
      { name: '작성자', value: message.author?.toString() || '알 수 없음', inline: true },
      { name: '채널', value: message.channel.toString(), inline: true },
      {
        name: '내용',
        value: message.content?.slice(0, 1024) || '*내용 없음*',
        inline: false,
      }
    );

  if (message.attachments.size > 0) {
    const attachments = message.attachments.map((att) => att.name).join('\n');
    embed.addFields({ name: '첨부파일', value: attachments, inline: false });
  }

  await logChannel.send({ embeds: [embed] });
}
