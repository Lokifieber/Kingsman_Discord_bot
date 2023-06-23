import os
import discord
import random
from discord.ext import tasks
from discord.ext import commands
from keep_alive import keep_alive
from commands_help import commands_help
from commands_meme import commands_meme
from commands_kleine import commands_kleine
from command_adminastriv import command_adminastriv
from commands_minigame import commands_minigame
from UserEvents import UserEvents

TOKEN = os.environ['DISCORD_BOT_SECRET']

bot = commands.Bot(command_prefix='!')
bot.remove_command("help")

@bot.event
async def on_ready():
    print(f'{bot.user.name} ist bereit!')
    await bot.change_presence(activity=discord.Game('!hilfe'))

bot.add_cog(commands_help(bot))
bot.add_cog(commands_meme(bot))
bot.add_cog(commands_kleine(bot))
bot.add_cog(command_adminastriv(bot))
bot.add_cog(commands_minigame(bot))
bot.add_cog(UserEvents(bot))

keep_alive()
bot.run(TOKEN)