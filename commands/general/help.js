import { SlashCommandBuilder, EmbedBuilder } from 'discord.js';

export const data = new SlashCommandBuilder()
  .setName('도움말')
  .setDescription('사용 가능한 명령어 목록을 확인합니다');

export async function execute(interaction) {
  const embed = new EmbedBuilder()
    .setTitle('📖 명령어 목록')
    .setColor(0x5865f2)
    .addFields(
      {
        name: '일반',
        value: '`/핑` `/정보` `/도움말` `/아바타` `/유저정보` `/서버정보`',
        inline: false,
      },
      {
        name: '관리자',
        value:
          '`/공지` `/임베드` `/추방` `/밴` `/언밴` `/타임아웃` `/경고` `/경고확인` `/경고초기화` `/restart` `/자동조정` `/욕설목록` `/백업` `/백업목록` `/백업복원` `/포인트관리`',
        inline: false,
      },
      {
        name: '티켓',
        value: '`/ticket` `/신고`',
        inline: false,
      },
      {
        name: '음악',
        value: '`/music` - play, queue, skip, nowplaying, loop, volume, on (관리자), off (관리자)',
        inline: false,
      },
      {
        name: '출석',
        value: '`/출석` `/출석현황` `/출석랭킹`',
        inline: false,
      }
    );

  await interaction.reply({ embeds: [embed] });
}
