import discord
import random
import asyncio
import csv
import time
from discord.ext import commands

class commands_minigame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rob_cooldown = {}
        self.player_data = {}
        self.load_data()

    @commands.command()
    async def stats(self, ctx):
        player_id = str(ctx.author.id)
        if player_id not in self.player_data:
            self.player_data[player_id] = {"money": 500000, "win": 0, "lose": 0}
        
        money = self.player_data[player_id]["money"]
        win = self.player_data[player_id]["win"]
        lose = self.player_data[player_id]["lose"]

        embed = discord.Embed(title="Dein Konto", color=0xFFD700)
        embed.add_field(name="Geld", value=f"{money} Euro", inline=False)
        embed.add_field(name="Gewinn", value=f"{win}", inline=True)
        embed.add_field(name="Verlust", value=f"{lose}", inline=True)
        await ctx.send(embed=embed)
        
    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        player_id = str(ctx.author.id)
        if player_id not in self.player_data:
            self.player_data[player_id] = {
                "money": 500000,
                "win": 0,
                "lose": 0
            }

        payout = 200000
        self.player_data[player_id]["money"] += payout
        self.save_data()

        embed = discord.Embed(title="Tägliche Auszahlung", color=0xFFD700)
        embed.add_field(name="Betrag", value=f"{payout} Euro", inline=False)
        embed.set_footer(text=f"Dein neuer Kontostand: {self.player_data[player_id]['money']} Euro")
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        sorted_players = sorted(self.player_data.items(), key=lambda x: x[1]["money"], reverse=True)
        leaderboard = []
        for index, (player_id, data) in enumerate(sorted_players[:10]):
            leaderboard.append(f"{index+1}. <@{player_id}> - Money: {data['money']} €")
        embed = discord.Embed(title="Leaderboard", color=0xFFD700)
        embed.description = "\n".join(leaderboard)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 14400, commands.BucketType.user)
    async def rob(self, ctx):
        player_id = str(ctx.author.id)
        if player_id not in self.player_data:
            self.player_data[player_id] = {"money": 500000, "win": 0, "lose": 0}
        
        events = {
            "Zentralbank": {"win": (250000, 500000, "Du hast den ultimativen Raubzug hingelegt und bewiesen, dass du ein Meisterdieb bist. (+1 Win)"),
                            "lose": (-500000, -100000, "Oh nein, du wurdest von der Polizei erwischt! Vielleicht warst du nicht schnell genug oder hast nicht vorsichtig genug gehandelt oder du bist einfach nur schlecht! (+1 Lose)")},
            "Bankfiliale": {"win": (100000, 250000, "Herzlichen Glückwunsch! Du hast es geschafft, die Bankfiliale erfolgreich auszurauben. Jetzt musst du schnell entkommen, bevor die Polizei dich erwischt. Hüte dich vor den Kameras und den Sicherheitsleuten, die dich aufspüren könnten. Aber pass auf, denn es wird nicht einfach sein, den ganzen Weg zurückzulegen und das gestohlene Geld zu behalten. (+1 Win)"),
                            "lose": (-250000, -100000, "Die Polizei hat dich nach einer wilden Verfolgungsjagd erwischt! Du solltest schneller sein oder bessere Fluchtstrategien entwickeln. (+1 Lose)")},
            "Juwelier": {"win": (100000, 250000, "Glückwunsch! Du hast erfolgreich den Juwelier ausgeraubt und die wertvollen Diamanten verkauft. Du bist ein Meisterdieb! (+1 Win)"),
                         "lose": (-250000, -100000, "Leider bist du beim Juwelier erwischt worden! Die Alarmanlage hat angeschlagen und die Polizei war schneller. (+1 Lose)")},
            "Farmer": {"win": (100000, 250000, "Du hast den Bauernhof erfolgreich ausgeraubt! Die Beute besteht aus wertvollen landwirtschaftlichen Geräten und Produkten. Gut gemacht! (+1 Win)"),
                       "lose": (-100000, -100000, "Der Bauer hat dich erwischt und die Polizei gerufen! Du bist in der Klemme. (+1 Lose)")},
            "Gruppierung": {"win": (0, 0, "Du hast erfolgreich die Geheimgesellschaft infiltriert und wichtige Informationen gestohlen. Du bist ein Meister der Tarnung! (+1 Win)"),
                            "lose": (-100000, -100000, "Die Gruppierung hat deine Identität")},
            "Bambi": {"win": (0, 0, "Du hast Bambi erfolgreich beklaut! Deine Skrupellosigkeit kennt keine Grenzen. (+1 Win)"),
                      "lose": (0, 0, "Wie ehrlos! Wie konntest du es wagen, Bambi zu bestehlen? Schäme dich! (+1 Lose)")}
        }    

        if player_id in self.rob_cooldown:
            remaining_time = self.rob_cooldown[player_id] - time.time()
            if remaining_time > 0:
                minutes, seconds = divmod(int(remaining_time), 60)
                await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")
                return

        event = random.choice(list(events.keys()))
        outcome = random.choice(["win", "lose"])
        payout = random.randint(events[event][outcome][0], events[event][outcome][1])
        event_text = events[event][outcome][2]

        if outcome == "win":
            self.player_data[player_id]["win"] += 1
            self.player_data[player_id]["money"] += payout
            embed = discord.Embed(title=f"Ausgeraubt: {event}", color=0xFFD700)
            embed.add_field(name="Erbeuteter Betrag", value=f"{payout} Euro", inline=False)
            embed.description = event_text
            embed.set_footer(text=f"Dein neuer Kontostand: {self.player_data[player_id]['money']} Euro")
            await ctx.send(embed=embed)
        else:
            self.player_data[player_id]["lose"] += 1
            self.player_data[player_id]["money"] += payout
            embed = discord.Embed(title=f"Gescheitert: {event}", color=0xFFD700)
            embed.add_field(name="Verlust", value=f"{abs(payout)} Euro", inline=False)
            embed.description = event_text
            embed.set_footer(text=f"Dein neuer Kontostand: {self.player_data[player_id]['money']} Euro")
            await ctx.send(embed=embed)

        self.rob_cooldown[player_id] = time.time() + 14400

        self.save_data()  # Speichert die Spielerdaten

    @rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = error.retry_after
            minutes, seconds = divmod(int(remaining_time), 60)
            await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")

    def save_data(self):
        with open('player_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["player_id", "money", "win", "lose"])
            for player_id, data in self.player_data.items():
                writer.writerow([player_id, data["money"], data["win"], data["lose"]])

    def load_data(self):
        try:
            with open('player_data.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    player_id = row["player_id"]
                    self.player_data[player_id] = {
                        "money": int(row["money"]),
                        "win": int(row["win"]),
                        "lose": int(row["lose"])
                    }
        except FileNotFoundError:
            pass
            
        self.save_data()

def setup(bot):
    bot.add_cog(commands_minigame(bot))