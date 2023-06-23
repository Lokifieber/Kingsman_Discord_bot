import discord
from discord.ext import commands
import random

class UserEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def robspieler(self, ctx, name):
        player_id = str(ctx.author.id)
        victim = None
        for member in ctx.guild.members:
            if member.display_name.lower() == name.lower():
                victim = member
                break
        
        if victim is None:
            await ctx.send("Spieler nicht gefunden.")
            return

        victim_id = str(victim.id)
        player_money = 0
        victim_money = 0
        
        # Überprüfen, ob Spielerdaten vorhanden sind, falls nicht, erstellen
        if player_id not in self.player_data:
            self.player_data[player_id] = {"money": 500000, "win": 0, "lose": 0}
        if victim_id not in self.player_data:
            self.player_data[victim_id] = {"money": 500000, "win": 0, "lose": 0}

        # Überprüfen, ob der Spieler bereits einen Raubüberfall durchgeführt hat
        if player_id in self.rob_cooldown:
            remaining_time = self.rob_cooldown[player_id] - time.time()
            if remaining_time > 0:
                minutes, seconds = divmod(int(remaining_time), 60)
                await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")
                return

        # Überprüfen, ob das Opfer bereits einen Raubüberfall durchgemacht hat
        if victim_id in self.rob_cooldown:
            remaining_time = self.rob_cooldown[victim_id] - time.time()
            if remaining_time > 0:
                minutes, seconds = divmod(int(remaining_time), 60)
                await ctx.send(f"{victim.display_name} ist noch {minutes} Minuten und {seconds} Sekunden vor einem weiteren Raubüberfall geschützt.")
                return

        player_money = self.player_data[player_id]["money"]
        victim_money = self.player_data[victim_id]["money"]

        # Überprüfen, ob der Spieler genügend Geld hat, um zu stehlen
        if player_money < 100000:
            await ctx.send("Du hast nicht genug Geld, um einen Raubüberfall zu starten.")
            return

        # Berechnen des Raubüberfall-Results
        success_chance = 20  # Erfolgschance des Raubüberfalls (20%)
        success = random.choices([True, False], weights=[success_chance, 100 - success_chance], k=1)[0]
        stolen_money = 0

        if success:
            stolen_percentage = random.randint(1, 100)  # Zufälliger Prozentsatz des Geldes, das gestohlen wird
            stolen_money = int(victim_money * stolen_percentage / 100)
            self.player_data[player_id]["money"] += stolen_money
            self.player_data[victim_id]["money"] -= stolen_money
            self.player_data[player_id]["win"] += 1
            self.player_data[victim_id]["lose"] += 1
            await ctx.send(f"{ctx.author.display_name} hat erfolgreich {victim.display_name} bestohlen und {stolen_money} Euro erbeutet!")
        else:
            loss_percentage = random.randint(1, 50)  # Zufälliger Prozentsatz des eigenen Geldes, das verloren geht
            loss_money = int(player_money * loss_percentage / 100)
            self.player_data[player_id]["money"] -= loss_money
            self.player_data[player_id]["lose"] += 1
            await ctx.send(f"{ctx.author.display_name} wurde erwischt! Du verlierst {loss_money} Euro.")

        # Setzen der Raubüberfall-Cooldowns für den Spieler und das Opfer
        self.rob_cooldown[player_id] = time.time() + 1800  # 1800 Sekunden = 30 Minuten
        self.rob_cooldown[victim_id] = time.time() + 1800  # 1800 Sekunden = 30 Minuten

        self.save_data()  # Speichern der Spielerdaten

def setup(bot):
    bot.add_cog(UserEvents(bot))
