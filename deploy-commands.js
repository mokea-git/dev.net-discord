import { REST, Routes } from 'discord.js';
import { readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { BOT_TOKEN, GUILD_ID, CLIENT_ID } from './config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const commands = [];
const commandsPath = join(__dirname, 'commands');
const commandFolders = readdirSync(commandsPath);

for (const folder of commandFolders) {
  const folderPath = join(commandsPath, folder);
  const commandFiles = readdirSync(folderPath).filter((file) => file.endsWith('.js'));

  for (const file of commandFiles) {
    const filePath = join(folderPath, file);
    const command = await import(`file://${filePath}`);

    if ('data' in command && 'execute' in command) {
      commands.push(command.data.toJSON());
      console.log(`✅ ${command.data.name} 명령어 로드됨`);
    }
  }
}

const rest = new REST().setToken(BOT_TOKEN);

(async () => {
  try {
    console.log(`\n📝 ${commands.length}개의 슬래시 커맨드를 등록합니다...`);

    const data = await rest.put(Routes.applicationGuildCommands(CLIENT_ID, GUILD_ID), {
      body: commands,
    });

    console.log(`✅ ${data.length}개의 슬래시 커맨드가 성공적으로 등록되었습니다!`);
  } catch (error) {
    console.error('❌ 커맨드 등록 중 오류 발생:', error);
  }
})();
