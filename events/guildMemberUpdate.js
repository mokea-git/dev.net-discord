import { Events, EmbedBuilder } from 'discord.js';
import { EXTENDED_LOG_CHANNEL_ID } from '../config.js';

export const name = Events.GuildMemberUpdate;

export async function execute(oldMember, newMember) {
  const logChannel = oldMember.guild.channels.cache.get(EXTENDED_LOG_CHANNEL_ID);
  if (!logChannel) return;

  // 닉네임 변경
  if (oldMember.displayName !== newMember.displayName) {
    const embed = new EmbedBuilder()
      .setTitle('👤 닉네임 변경')
      .setColor(0x0000ff)
      .addFields(
        { name: '유저', value: newMember.toString(), inline: true },
        { name: '변경 전', value: oldMember.displayName, inline: true },
        { name: '변경 후', value: newMember.displayName, inline: true }
      );

    await logChannel.send({ embeds: [embed] });
  }

  // 역할 변경
  const oldRoles = oldMember.roles.cache;
  const newRoles = newMember.roles.cache;

  if (oldRoles.size !== newRoles.size || !oldRoles.equals(newRoles)) {
    const addedRoles = newRoles.filter((role) => !oldRoles.has(role.id) && role.name !== '@everyone');
    const removedRoles = oldRoles.filter((role) => !newRoles.has(role.id) && role.name !== '@everyone');

    if (addedRoles.size > 0 || removedRoles.size > 0) {
      const embed = new EmbedBuilder()
        .setTitle('🎭 역할 변경')
        .setColor(0x800080)
        .addFields({ name: '유저', value: newMember.toString(), inline: false });

      if (addedRoles.size > 0) {
        embed.addFields({
          name: '추가된 역할',
          value: addedRoles.map((r) => r.toString()).join(' '),
          inline: false,
        });
      }

      if (removedRoles.size > 0) {
        embed.addFields({
          name: '제거된 역할',
          value: removedRoles.map((r) => r.toString()).join(' '),
          inline: false,
        });
      }

      await logChannel.send({ embeds: [embed] });
    }
  }
}
