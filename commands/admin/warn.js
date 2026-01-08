import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import { PUNISH_LOG_CHANNEL_ID } from '../../config.js';
import { readFileSync, writeFileSync, existsSync } from 'fs';

const WARNINGS_FILE = './warnings.json';

function loadWarnings() {
  if (existsSync(WARNINGS_FILE)) {
    return JSON.parse(readFileSync(WARNINGS_FILE, 'utf-8'));
  }
  return {};
}

function saveWarnings(warnings) {
  writeFileSync(WARNINGS_FILE, JSON.stringify(warnings, null, 2));
}

export const data = new SlashCommandBuilder()
  .setName('경고')
  .setDescription('유저에게 경고를 부여합니다')
  .setDefaultMemberPermissions(PermissionFlagsBits.Administrator)
  .addUserOption((option) => option.setName('유저').setDescription('경고할 유저').setRequired(true))
  .addStringOption((option) => option.setName('사유').setDescription('경고 사유').setRequired(false));

export async function execute(interaction) {
  const user = interaction.options.getUser('유저');
  const 사유 = interaction.options.getString('사유') || '사유 없음';

  const warnings = loadWarnings();
  const userId = user.id;

  if (!warnings[userId]) {
    warnings[userId] = [];
  }

  warnings[userId].push({
    reason: 사유,
    by: interaction.user.username,
    time: new Date().toLocaleString('ko-KR'),
  });

  saveWarnings(warnings);

  const warnCount = warnings[userId].length;

  // DM 전송 시도
  try {
    const dmEmbed = new EmbedBuilder()
      .setTitle('⚠️ 경고를 받았습니다')
      .setDescription(`**${interaction.guild.name}** 서버에서 경고를 받았습니다.`)
      .setColor(0xffa500)
      .addFields(
        { name: '사유', value: 사유, inline: false },
        { name: '누적 경고', value: `${warnCount}회`, inline: true }
      );

    await user.send({ embeds: [dmEmbed] });
  } catch (error) {
    // DM 전송 실패 무시
  }

  const embed = new EmbedBuilder()
    .setTitle('⚠️ 경고')
    .setColor(0xffa500)
    .addFields(
      { name: '경고 받은 유저', value: user.toString(), inline: true },
      { name: '누적 경고', value: `${warnCount}회`, inline: true },
      { name: '사유', value: 사유, inline: false }
    )
    .setFooter({ text: `처리자: ${interaction.user.username}` });

  await interaction.reply({ embeds: [embed] });

  // 로그 채널에 기록
  const logChannel = interaction.guild.channels.cache.get(PUNISH_LOG_CHANNEL_ID);
  if (logChannel) {
    const logEmbed = new EmbedBuilder()
      .setTitle('⚠️ 경고')
      .setDescription(`**${user.username}**님이 경고를 받았습니다.`)
      .setColor(0xffa500)
      .setTimestamp()
      .addFields(
        { name: '대상', value: user.toString(), inline: true },
        { name: '누적 경고', value: `${warnCount}회`, inline: true },
        { name: '처리자', value: interaction.user.toString(), inline: true },
        { name: '사유', value: 사유, inline: false }
      );

    await logChannel.send({ embeds: [logEmbed] });
  }

  if (warnCount >= 3) {
    await interaction.channel.send(`⚠️ ${user}님이 경고 ${warnCount}회에 도달했습니다!`);
  }
}
