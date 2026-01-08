import { Events, ActivityType, PresenceUpdateStatus } from 'discord.js';

export const name = Events.ClientReady;
export const once = true;

export async function execute(client) {
  console.log(`We have logged in as ${client.user.tag}`);

  // 상태 설정
  client.user.setPresence({
    status: PresenceUpdateStatus.DoNotDisturb,
    activities: [
      {
        name: '생각중...',
        type: ActivityType.Listening,
      },
    ],
  });
}
