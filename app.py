import nextcord
from nextcord.ext import commands

from config import BOT_TOKEN

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Cogs 로드
bot.load_extension("events")
bot.load_extension("commands.admin")
bot.load_extension("commands.general")
bot.load_extension("commands.ticket")
bot.load_extension("commands.music")
bot.load_extension("commands.automod")
bot.load_extension("commands.backup")
bot.load_extension("commands.attendance")

bot.run(BOT_TOKEN)