import discord
import random
from discord.ext import tasks
from discord.ext import commands

class commands_kleine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bademeister(self, ctx):
        await ctx.send('Die russischen Wurzeln schlagen bei ihm stark durch, nicht nur in der Grammatik. Wird als Ziv wohl häufiger mit seinem Cop-Namen angesprochen, als mit seinem richtigen. Im Herzen ist auch er in der Abteilung Queensman.')
    
    @commands.command()
    async def zauberfee(self, ctx):
        await ctx.send('Die lokale Fee für alles, Tier- und Taschenlampen-Fanatikerin und ebenfalls Abteilung Queensman. Schießt bisher nicht, mal schauen wie lange noch...')
    
    @commands.command()
    async def farmrad(self, ctx):
        await ctx.send('Eigentlich HTHT-Randale Fan, irgendwann aber zum Farmer mutiert. Gibts nur im Doppelpack mit Erik. Spezialfähigkeit: Kann hören was Erik isst.')

    @commands.command()
    async def blitzermeister(self, ctx):
        await ctx.send('Wohl der beste Fluchtwagenfahrer den man finden kann. Blitzt als Justizler zur großen Freude aller alles was nicht bei drei auf den Bäumen ist. Wir lieben ihn trotzdem.')
    
    @commands.command()
    async def farmrich(self, ctx):
        await ctx.send('Inoffizieller Inhaber der Gang, wird irgendwann Bademeister sägen. Steht auf Blondinen. Auch ihn gibts nur im Doppelpack mit Fahrrad.')
    
    @commands.command()
    async def weizenkönigin(self, ctx):
        await ctx.send('Gehört zur Abteilung Queensman und ist Fake-Blondine. Mal mehr, mal weniger da, aber immer mit der selben Message: Weizen lohnt sich!')
    
    @commands.command()
    async def tomtom(self, ctx):
        await ctx.send('Bademeisters Sohn und wohl kriminellstes Bambi. Am ersten Tag schon in einer Gang gewesen, damit ist er Rekordhalter.')
    
    @commands.command()
    async def nachohonor(self, ctx):
        await ctx.send('Eigentlich sollte das hier über Rick sein. Nacho ist aber der Maincharakter, sorry. We love Nacho! (Rick ist aber auch cool, vorallem als Inhaber der "Elektrofreunde".)') 
    
    @commands.command()
    async def nordsüdwest(self, ctx):
        await ctx.send('Hoch abwesender Mapper, im Doppelpack mit Westermann unerträglich.')
    
    @commands.command()
    async def hotzenbrotz(self, ctx):
        await ctx.send('Räuber Hotzenplotz, aber bayrisch. Autoklauprofi und bei der Justiz diskutierender Stammgast. (Und hauptsächlich Farmer, er schreibt über alles Exceltabellen, der Schwitzer.)')
    
    @commands.command()
    async def maseratiulf(self, ctx):
        await ctx.send('Der Kiez-Boss, das Zentrum des Wissens. Ausgestattet mit Überfallmich-Gesicht und der schlimmen Frisur. Hier ist reiner Drip zu finden.')
        
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

    @commands.command()
    async def tableflip(self, ctx, *, message):
        flipped_message = f"{message} (╯°□°）╯︵ ┻━┻"
        await ctx.send(flipped_message)
    
    @commands.command()
    async def unflip(self, ctx, *, message):
        flipped_message = f"{message} ┬─┬ ノ( ゜-゜ノ)"
        await ctx.send(flipped_message)
    
    @commands.command()
    async def shrug(self, ctx, *, message):
        shrug_message = f"{message}¯\_(ツ)_/¯"
        await ctx.send(shrug_message)
    
def setup(bot):
    bot.add_cog(commands_kleine(bot))