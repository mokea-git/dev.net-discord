import { Client, GatewayIntentBits, Partials, Collection } from 'discord.js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readdirSync } from 'fs';
import { BOT_TOKEN } from './config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 클라이언트 생성
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildPresences,
    GatewayIntentBits.MessageContent,
  ],
  partials: [Partials.Channel, Partials.GuildMember, Partials.Message, Partials.User],
});

// 명령어 컬렉션
client.commands = new Collection();

// 이벤트 로더
const eventsPath = join(__dirname, 'events');
const eventFiles = readdirSync(eventsPath).filter((file) => file.endsWith('.js'));

for (const file of eventFiles) {
  const filePath = join(eventsPath, file);
  const event = await import(`file://${filePath}`);

  if (event.once) {
    client.once(event.name, (...args) => event.execute(...args, client));
  } else {
    client.on(event.name, (...args) => event.execute(...args, client));
  }
  console.log(`[이벤트] ${event.name} 로드됨`);
}

// 명령어 로더
const commandsPath = join(__dirname, 'commands');
const commandFolders = readdirSync(commandsPath);

for (const folder of commandFolders) {
  const folderPath = join(commandsPath, folder);
  const commandFiles = readdirSync(folderPath).filter((file) => file.endsWith('.js'));

  for (const file of commandFiles) {
    const filePath = join(folderPath, file);
    const command = await import(`file://${filePath}`);

    if ('data' in command && 'execute' in command) {
      client.commands.set(command.data.name, command);
      console.log(`[명령어] ${command.data.name} 로드됨`);
    }
  }
}

// 봇 로그인
client.login(BOT_TOKEN);
