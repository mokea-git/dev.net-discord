import { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } from 'discord.js';
import {
  joinVoiceChannel,
  createAudioPlayer,
  createAudioResource,
  AudioPlayerStatus,
  VoiceConnectionStatus,
  entersState,
} from '@discordjs/voice';
import play from 'play-dl';
import { MUSIC_VOICE_CHANNEL_ID, ADMIN_ROLE_ID } from '../../config.js';

const musicQueue = new Map();
let globalConnection = null;
let globalPlayer = null;

export const data = new SlashCommandBuilder()
  .setName('music')
  .setDescription('음악 기능을 사용합니다')
  .addStringOption((option) =>
    option
      .setName('action')
      .setDescription('기능 선택')
      .setRequired(true)
      .addChoices(
        { name: 'on - 봇 입장 (관리자)', value: 'on' },
        { name: 'off - 봇 퇴장 (관리자)', value: 'off' },
        { name: 'play - 음악 재생', value: 'play' },
        { name: 'queue - 재생목록 확인', value: 'queue' },
        { name: 'skip - 다음 곡', value: 'skip' },
        { name: 'nowplaying - 현재 재생중', value: 'nowplaying' },
        { name: 'volume - 볼륨 조절', value: 'volume' }
      )
  )
  .addStringOption((option) =>
    option.setName('url').setDescription('유튜브 링크 또는 검색어').setRequired(false)
  );

export async function execute(interaction) {
  const action = interaction.options.getString('action');
  const url = interaction.options.getString('url');

  const guildId = interaction.guildId;

  switch (action) {
    case 'on':
      await handleOn(interaction);
      break;
    case 'off':
      await handleOff(interaction);
      break;
    case 'play':
      await handlePlay(interaction, url, guildId);
      break;
    case 'queue':
      await handleQueue(interaction, guildId);
      break;
    case 'skip':
      await handleSkip(interaction, guildId);
      break;
    case 'nowplaying':
      await handleNowPlaying(interaction, guildId);
      break;
    case 'volume':
      await handleVolume(interaction, url, guildId);
      break;
    default:
      await interaction.reply({ content: '잘못된 기능입니다.', ephemeral: true });
  }
}

async function handleOn(interaction) {
  // 관리자 확인
  if (!interaction.member.roles.cache.has(ADMIN_ROLE_ID)) {
    await interaction.reply({ content: '❌ 관리자만 사용할 수 있습니다.', ephemeral: true });
    return;
  }

  const voiceChannel = interaction.guild.channels.cache.get(MUSIC_VOICE_CHANNEL_ID);

  if (!voiceChannel) {
    await interaction.reply({ content: '음성 채널을 찾을 수 없습니다.', ephemeral: true });
    return;
  }

  if (globalConnection) {
    await interaction.reply({ content: '이미 음성 채널에 있습니다.', ephemeral: true });
    return;
  }

  globalConnection = joinVoiceChannel({
    channelId: voiceChannel.id,
    guildId: interaction.guildId,
    adapterCreator: interaction.guild.voiceAdapterCreator,
  });

  globalPlayer = createAudioPlayer();
  globalConnection.subscribe(globalPlayer);

  await interaction.reply(`🔊 **${voiceChannel.name}** 채널에 입장했습니다!`);
}

async function handleOff(interaction) {
  // 관리자 확인
  if (!interaction.member.roles.cache.has(ADMIN_ROLE_ID)) {
    await interaction.reply({ content: '❌ 관리자만 사용할 수 있습니다.', ephemeral: true });
    return;
  }

  if (!globalConnection) {
    await interaction.reply({ content: '봇이 음성 채널에 없습니다.', ephemeral: true });
    return;
  }

  globalPlayer?.stop();
  globalConnection.destroy();
  globalConnection = null;
  globalPlayer = null;
  musicQueue.delete(interaction.guildId);

  await interaction.reply('🔇 음악을 멈추고 퇴장했습니다.');
}

async function handlePlay(interaction, url, guildId) {
  if (!globalConnection) {
    await interaction.reply({ content: '먼저 관리자가 `on`으로 봇을 입장시켜야 합니다.', ephemeral: true });
    return;
  }

  if (!url) {
    await interaction.reply({ content: '유튜브 링크 또는 검색어를 입력해주세요.', ephemeral: true });
    return;
  }

  await interaction.deferReply();

  try {
    let videoInfo;

    // YouTube 링크인지 확인
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      videoInfo = await play.video_info(url);
    } else {
      // 검색어로 처리
      const searched = await play.search(url, { limit: 1 });
      if (searched.length === 0) {
        await interaction.followUp('검색 결과를 찾을 수 없습니다.');
        return;
      }
      videoInfo = await play.video_info(searched[0].url);
    }

    const songData = {
      title: videoInfo.video_details.title,
      url: videoInfo.video_details.url,
      thumbnail: videoInfo.video_details.thumbnails[0]?.url,
      duration: videoInfo.video_details.durationInSec,
      requester: interaction.user,
    };

    if (!musicQueue.has(guildId)) {
      musicQueue.set(guildId, []);
    }

    const queue = musicQueue.get(guildId);

    if (globalPlayer.state.status === AudioPlayerStatus.Playing || queue.length > 0) {
      queue.push(songData);
      const embed = new EmbedBuilder()
        .setTitle('➕ 재생목록에 추가됨')
        .setDescription(`**${songData.title}**`)
        .setColor(0x0000ff)
        .addFields({ name: '대기열 위치', value: `${queue.length}번째`, inline: true })
        .setFooter({ text: `요청자: ${interaction.user.username}` });

      if (songData.thumbnail) embed.setThumbnail(songData.thumbnail);

      await interaction.followUp({ embeds: [embed] });
    } else {
      await playSong(songData, interaction, guildId);

      const embed = new EmbedBuilder()
        .setTitle('▶️ 재생 시작')
        .setDescription(`**${songData.title}**`)
        .setColor(0x00ff00)
        .setFooter({ text: `요청자: ${interaction.user.username}` });

      if (songData.thumbnail) embed.setThumbnail(songData.thumbnail);

      await interaction.followUp({ embeds: [embed] });
    }
  } catch (error) {
    console.error(error);
    await interaction.followUp(`오류가 발생했습니다: ${error.message}`);
  }
}

async function playSong(songData, interaction, guildId) {
  try {
    const stream = await play.stream(songData.url);
    const resource = createAudioResource(stream.stream, { inputType: stream.type });

    globalPlayer.play(resource);

    globalPlayer.once(AudioPlayerStatus.Idle, async () => {
      const queue = musicQueue.get(guildId);
      if (queue && queue.length > 0) {
        const nextSong = queue.shift();
        await playSong(nextSong, interaction, guildId);

        const embed = new EmbedBuilder()
          .setTitle('▶️ 다음 곡 재생')
          .setDescription(`**${nextSong.title}**`)
          .setColor(0x00ff00)
          .setFooter({ text: `요청자: ${nextSong.requester.username}` });

        if (nextSong.thumbnail) embed.setThumbnail(nextSong.thumbnail);

        await interaction.channel.send({ embeds: [embed] });
      }
    });
  } catch (error) {
    console.error('재생 오류:', error);
  }
}

async function handleQueue(interaction, guildId) {
  const queue = musicQueue.get(guildId) || [];

  if (queue.length === 0) {
    await interaction.reply({ content: '재생목록이 비어있습니다.', ephemeral: true });
    return;
  }

  const embed = new EmbedBuilder().setTitle('🎵 재생목록').setColor(0x800080);

  let queueText = '';
  for (let i = 0; i < Math.min(queue.length, 10); i++) {
    queueText += `\`${i + 1}.\` ${queue[i].title}\n`;
  }

  embed.addFields({
    name: `⏭️ 대기 중 (${queue.length}곡)`,
    value: queueText,
    inline: false,
  });

  await interaction.reply({ embeds: [embed], ephemeral: true });
}

async function handleSkip(interaction, guildId) {
  if (!globalPlayer || globalPlayer.state.status !== AudioPlayerStatus.Playing) {
    await interaction.reply({ content: '재생 중인 곡이 없습니다.', ephemeral: true });
    return;
  }

  globalPlayer.stop();
  await interaction.reply('⏭️ 다음 곡으로 넘어갑니다.');
}

async function handleNowPlaying(interaction, guildId) {
  // 현재 재생중인 곡 정보는 별도로 저장해야 합니다
  await interaction.reply({ content: '현재 재생 중인 곡 정보를 불러올 수 없습니다.', ephemeral: true });
}

async function handleVolume(interaction, volumeStr, guildId) {
  await interaction.reply({ content: '볼륨 조절 기능은 개발 중입니다.', ephemeral: true });
}
