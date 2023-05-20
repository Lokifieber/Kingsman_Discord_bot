import discord
from discord.ext import commands
import random


class commands_meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def meme(self, ctx):
        channel = self.bot.get_channel(1079840050671534083)
        messages = await channel.history(limit=9000).flatten()
        image_messages = [msg for msg in messages if len(msg.attachments) > 0]
        random_message = random.choice(image_messages)
        embed = discord.Embed(title=random_message.content,
                              color=discord.Color.gold())
        embed.set_image(url=random_message.attachments[0].url)
        await ctx.send(embed=embed)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(commands_meme(bot))
