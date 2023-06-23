import discord
from discord.ext import commands

class commands_help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hilfe(self, ctx):
        embeds = [
            discord.Embed(title="Hilfe - Seite 1 - Allgemeine Commands", description="Hier sind die verfügbaren Befehle:", color=0xFFD700),
            discord.Embed(title="Hilfe - Seite 2", description="Hier sind noch mehr Befehle:", color=0xFFD700),
            discord.Embed(title="Hilfe - Seite 3 - Minigame/Unterhaltung", description="Und hier noch ein paar mehr:", color=0xFFD700),
            discord.Embed(title="Hilfe - Seite 4 - Credits", description="Information", color=0xFFD700),
            discord.Embed(title="Hilfe - Seite 5 - Die Gang", description="Die GANG", color=0xFFD700)
        ]

        embeds[0].add_field(name="!ping", value="Zeigt die aktuelle Latenz des Bots an.", inline=False)
        embeds[0].add_field(name="!info", value="Zeigt Informationen über den Server an.", inline=False)
        embeds[0].add_field(name="!flip", value="Wirft eine Münze.", inline=False)
        embeds[0].add_field(name="!vote <Titel>", value="Erstellt eine Umfrage mit Emojis als Reaktionen.", inline=False)
        embeds[0].add_field(name="!closevote <Nachrichten-ID>", value="Schließt eine Umfrage und gibt das Ergebnis aus.", inline=False)
        embeds[0].add_field(name="!uptime", value="Zeigt an, wie lange der Bot bereits mit Discord verbunden ist.", inline=False)
        embeds[0].add_field(name="!hallo", value="Sagt hallo zurück.", inline=False)
        embeds[2].add_field(name="!meme", value="Für hochklassifizierte Kingsman Memes.", inline=False)
        embeds[2].add_field(name="!stats", value="Um deine Statistik einzusehen.", inline=False)
        embeds[2].add_field(name="!rob", value="Startet ein Event, um etwas zu rauben.", inline=False)
        embeds[2].add_field(name="!robuser @user", value="Raub ein Spieler aus.", inline=False)
        embeds[2].add_field(name="!coinflip [Einsatz]", value="Wirft eine Münze mit Geld.", inline=False)
        embeds[2].add_field(name="!transferm @User [Betrag]", value="Geld überweisen an andern Spieler", inline=False)
        embeds[2].add_field(name="!leaderboard", value="Top 10 Spieler.", inline=False)
        embeds[2].add_field(name="Version Minigame:", value="0.3", inline=False)
        embeds[3].add_field(name="Author", value="Loki Fieber", inline=False)
        embeds[3].add_field(name="Version", value="1.2", inline=False)
        embeds[3].add_field(name="Discord-Link", value="https://discord.com/users/DEINE_DISCORD_ID", inline=False)
        embeds[3].add_field(name="GitHub-Link", value="https://github.com/DEIN_GITHUB_USERNAME/DEIN_REPOSITORY", inline=False)
        embeds[4].add_field(name="!bademeister", value="Patrick Bateman", inline=False)
        embeds[4].add_field(name="!zauberfee", value="Laura Brotz", inline=False)
        embeds[4].add_field(name="!farmrad", value="Fard Muruk", inline=False)
        embeds[4].add_field(name="!blitzermeister", value="Yannik Herrmann", inline=False)
        embeds[4].add_field(name="!farmrich", value="Erik van Tohr", inline=False)
        embeds[4].add_field(name="!weizenkönigin", value="Antonia Weimar", inline=False)
        embeds[4].add_field(name="!tomtom", value="Tom Legat", inline=False)
        embeds[4].add_field(name="!nachohonor", value="Rick Honor", inline=False)
        embeds[4].add_field(name="!nordsüdwest", value="Werner Nord", inline=False)
        embeds[4].add_field(name="!hotzenbrotz", value="Lukas Brotz", inline=False)
        embeds[4].add_field(name="!maseratiulf", value="Ulf Zwielichtig", inline=False)

        paginator = Paginator(ctx, embeds)
        await paginator.run()

        await ctx.message.delete()

class Paginator:
    def __init__(self, ctx, embeds, timeout=60):
        self.ctx = ctx
        self.embeds = embeds
        self.timeout = timeout
        self.page = 0
        self.reactions = ['⬅️', '➡️', '❌']

    async def run(self):
        message = await self.ctx.send(embed=self.embeds[self.page])
        for reaction in self.reactions:
            await message.add_reaction(reaction)

        def check(reaction, user):
            return user == self.ctx.author and str(reaction.emoji) in self.reactions

        while True:
            try:
                reaction, user = await self.ctx.bot.wait_for('reaction_add', timeout=self.timeout, check=check)
            except:
                for reaction in self.reactions:
                    await message.remove_reaction(reaction, self.ctx.bot.user)
                break

            if str(reaction.emoji) == '⬅️':
                if self.page > 0:
                    self.page -= 1
                    await message.edit(embed=self.embeds[self.page])
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == '➡️':
                if self.page < len(self.embeds) - 1:
                    self.page += 1
                    await message.edit(embed=self.embeds[self.page])
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == '❌':
                for reaction in self.reactions:
                    await message.remove_reaction(reaction, self.ctx.bot.user)
                break

def setup(bot):
    bot.add_cog(commands_help(bot))