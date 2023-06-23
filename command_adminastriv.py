import discord
import datetime
from discord.ext import commands

class command_adminastriv(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx):
        server = ctx.guild
        embed = discord.Embed(title=server.name, description="Server-Informationen", color=discord.Color.blue())
        embed.set_thumbnail(url=server.icon_url)
        embed.add_field(name="Server erstellt am", value=server.created_at.strftime("%d.%m.%Y um %H:%M:%S"), inline=True)
        embed.add_field(name="Server-Region", value=str(server.region), inline=True)
        embed.add_field(name="Anzahl Mitglieder", value=server.member_count, inline=True)
        embed.add_field(name="Owner", value=server.owner, inline=True)
        embed.add_field(name="Server ID", value=server.id, inline=True)
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command()
    async def vote(self, ctx, *, question):
        message = await ctx.send(f"{ctx.author.mention} Abstimmung: {question}")
        await message.add_reaction("👍")
        await message.add_reaction("👎")

    @commands.command()
    async def closevote(self, ctx, message_id: int):
        message = await ctx.fetch_message(message_id)
        await message.clear_reactions()
        await self.show_result(message, ctx)
       
    @commands.command()
    async def uptime(self, ctx):
        delta = datetime.datetime.utcnow() - self.bot.start_time
        uptime = str(delta).split(".")[0]
        await ctx.send(f"I have been connected for {uptime}.")
        
    async def show_result(self, message, ctx):
        reactions = message.reactions
        upvotes = 0
        downvotes = 0
        for reaction in reactions:
            if str(reaction.emoji) == '👍':
                upvotes = reaction.count - 1 # don't count the bot's reaction
            elif str(reaction.emoji) == '👎':
                downvotes = reaction.count - 1 # don't count the bot's reaction
        result_embed = discord.Embed(title="Ergebnis der Abstimmung:", description=f"{upvotes} 👍, {downvotes} 👎", color=discord.Color.blue())
        await ctx.send(embed=result_embed)

def setup(bot):
    bot.add_cog(command_adminastriv(bot))