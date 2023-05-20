import discord
import random
from discord.ext import tasks
from discord.ext import commands

class commands_kleine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def Bademeister(self, ctx):
      await ctx.send('Die Geschichte von Patrick Bateman ist eine beängstigende und verstörende Darstellung von einem Mann, der von seiner eigenen Perfektion besessen ist und durch seine psychopathischen Tendenzen immer tiefer in eine Spirale aus Gewalt und Grausamkeit gerät.')
      await ctx.message.delete()

    @commands.command()
    async def hallo(self, ctx):
      await ctx.send(f'Hallo, {ctx.author}!')
	
    @commands.command()
    async def ping(self, ctx):
      await ctx.send(f'Pong! Latenz: {round(self.bot.latency * 1000)}ms')
	
    @commands.command()
    async def flip(self, ctx):
      result = random.choice(["Kopf", "Zahl"])
      await ctx.send(f"{ctx.author.mention} {result}!") 

def setup(bot):
    bot.add_cog(commands_kleine(bot))