import { Events } from 'discord.js';

export const name = Events.InteractionCreate;

export async function execute(interaction, client) {
  // 슬래시 명령어 처리
  if (interaction.isChatInputCommand()) {
    const command = client.commands.get(interaction.commandName);

    if (!command) {
      console.error(`명령어 ${interaction.commandName}를 찾을 수 없습니다.`);
      return;
    }

    try {
      await command.execute(interaction);
    } catch (error) {
      console.error('명령어 실행 중 오류:', error);
      const errorMessage = {
        content: '명령어 실행 중 오류가 발생했습니다!',
        ephemeral: true,
      };

      if (interaction.replied || interaction.deferred) {
        await interaction.followUp(errorMessage);
      } else {
        await interaction.reply(errorMessage);
      }
    }
  }

  // 버튼 상호작용 처리
  if (interaction.isButton()) {
    // 버튼 핸들러는 각 명령어 파일에서 처리
  }

  // 모달 제출 처리
  if (interaction.isModalSubmit()) {
    // 모달 핸들러는 각 명령어 파일에서 처리
  }
}
