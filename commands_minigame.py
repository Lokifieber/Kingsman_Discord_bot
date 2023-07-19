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
        self.daily_cooldown = {}
        self.robuser_cooldown = {}
        self.player_data = {}
        self.load_data()

    @commands.command()
    async def stats(self, ctx):
        player_id = str(ctx.author.id)
        if player_id not in self.player_data:
            self.player_data[player_id] = {"money": 500000, "win": 0, "lose": 0, "last_daily": 0, "streak": 0}
        
        money = self.player_data[player_id]["money"]
        win = self.player_data[player_id]["win"]
        lose = self.player_data[player_id]["lose"]

        embed = discord.Embed(title="Dein Konto", color=0xFFD700)
        embed.add_field(name="Geld", value=f"{money} Euro", inline=False)
        await ctx.send(embed=embed)
        
    @commands.command()
    async def daily(self, ctx):
        player_id = str(ctx.author.id)
        if player_id not in self.player_data:
            self.player_data[player_id] = {
                "money": 500000,
                "win": 0,
                "lose": 0,
                "last_daily": 0,
                "streak": 0
            }

        if player_id in self.rob_cooldown:
            remaining_time = self.rob_cooldown[player_id] - time.time()
            if remaining_time > 0:
                minutes, seconds = divmod(int(remaining_time), 60)
                await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bis du deinen Täglichen Strike abholen kannst.")
                return

        current_time = time.time()
        last_daily = self.player_data[player_id]["last_daily"]
        if current_time - last_daily >= 86400:  # 24 hours in seconds
            self.player_data[player_id]["last_daily"] = current_time
            self.player_data[player_id]["streak"] += 1
            if self.player_data[player_id]["streak"] >= 10:
                self.player_data[player_id]["streak"] = 0
                self.player_data[player_id]["money"] += 1000000
                payout = 1000000
                await ctx.send("Herzlichen Glückwunsch! Du hast deinen Täglichen Strike für 10 Tage in Folge erreicht und erhältst 1.000.000 Euro!")
            else:
                self.player_data[player_id]["money"] += 100000
                payout = 100000
                await ctx.send("Du hast deinen Täglichen Strike erreicht und erhältst 100.000 Euro!")
        else:
            remaining_time = 86400 - (current_time - last_daily)
            minutes, seconds = divmod(int(remaining_time), 60)
            await ctx.send(f"Du hast deinen Täglichen Strike bereits abgeholt. Bitte warte {minutes} Minuten und {seconds} Sekunden, um ihn erneut abzuholen.")
            return

        money = self.player_data[player_id]["money"]
        streak = self.player_data[player_id]["streak"]

        embed = discord.Embed(title="Täglicher Strike", color=0xFFD700)
        embed.add_field(name="Auszahlung", value=f"{payout} Euro", inline=False)
        embed.add_field(name="Aktuelle Streak", value=f"{streak}/10", inline=True)
        embed.add_field(name="Aktuelles Konto", value=f"{money} Euro", inline=True)
        await ctx.send(embed=embed)

        self.save_data()

    @commands.command()
    async def reset(self, ctx):
        player_id = str(ctx.author.id)
        if player_id not in self.player_data:
            await ctx.send("Du hast noch keinen Täglichen Strike gesammelt.")
            return

        self.player_data[player_id]["streak"] = 0
        self.save_data()
        await ctx.send("Dein Täglicher Strike wurde zurückgesetzt.")
    
    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = error.retry_after
            hours, remainder = divmod(int(remaining_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"Du musst noch {hours} Stunden, {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")
            
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
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def rob(self, ctx):
        player_id = str(ctx.author.id)
        if player_id not in self.player_data:
            self.player_data[player_id] = {"money": 500000, "win": 0, "lose": 0, "last_daily": 0, "streak": 0}

        if player_id in self.rob_cooldown:
            remaining_time = self.rob_cooldown[player_id] - time.time()
            if remaining_time > 0:
                minutes, seconds = divmod(int(remaining_time), 60)
                await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")
                return

        # Ausrüstungs-Optionen hinzufügen
        equipment_options = {
            "🔫": {"name": "Pistole und eine einfache Weste", "cost": 50000, "chance": 0.4},
            "🃏": {"name": "AR-15 Kit mit einer guten Rebellenweste", "cost": 100000, "chance": 0.5},
            "🧨": {"name": "7,62 MDR Kit und Kampfausrüstung", "cost": 200000, "chance": 0.6}
        }

        # Ausrüstungs-Nachricht senden und Reaktionen hinzufügen
        equipment_message = await ctx.send("Wähle eine Ausrüstung aus (oder reagiere mit ✅ für keinen Einsatz):")
        for emoji, equipment in equipment_options.items():
            await equipment_message.add_reaction(emoji)
            await ctx.send(f"{emoji} - {equipment['name']} (Kosten: {equipment['cost']})")
        await equipment_message.add_reaction("✅")

        def check(reaction, user):
            return user == ctx.author and (str(reaction.emoji) in equipment_options.keys() or str(reaction.emoji) == "✅") and reaction.message.id == equipment_message.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Du hast nicht innerhalb von 30 Sekunden reagiert. Der Raubzug wurde abgebrochen.")
            return

        selected_equipment = equipment_options.get(str(reaction.emoji))
        if selected_equipment:
            equipment_name = selected_equipment["name"]
            equipment_cost = selected_equipment["cost"]
            win_chance = selected_equipment["chance"]
        else:
            equipment_name = "Keine Ausrüstung"
            equipment_cost = 0
            win_chance = 0.3  # Standard-Gewinnchance ohne Ausrüstung

        if self.player_data[player_id]["money"] < equipment_cost:
            await ctx.send("Du hast nicht genug Geld, um diese Ausrüstung zu kaufen.")
            return

        self.player_data[player_id]["money"] -= equipment_cost

        await ctx.send("Es wird nach Beute gesucht... (Dauer: 30 Sekunden)")
        await asyncio.sleep(30)

        events = [
            ("Zentralbank", {"win": (300000, 800000, "Du hast den ultimativen Raubzug hingelegt und bewiesen, dass du ein Meisterdieb bist. (+1 Win)"),
                    "lose": (-500000, -100000, "Oh nein, du wurdest von der Polizei erwischt! Vielleicht warst du nicht schnell genug oder hast nicht vorsichtig genug gehandelt oder du bist einfach nur schlecht! (+1 Lose)")}),
            ("Bankfiliale", {"win": (250000, 500000, "Herzlichen Glückwunsch! Du hast es geschafft, die Bankfiliale erfolgreich auszurauben. Jetzt musst du schnell entkommen, bevor die Polizei dich erwischt. Hüte dich vor den Kameras und den Sicherheitsleuten, die dich aufspüren könnten. Aber pass auf, denn es wird nicht einfach sein, den ganzen Weg zurückzulegen und das gestohlene Geld zu behalten. (+1 Win)"),
                    "lose": (-250000, -100000, "Die Polizei hat dich nach einer wilden Verfolgungsjagd erwischt! Du solltest schneller sein oder bessere Fluchtstrategien entwickeln. (+1 Lose)")}),
            ("Juwelier", {"win": (100000, 450000, "Glückwunsch! Du hast erfolgreich den Juwelier ausgeraubt und die wertvollen Diamanten verkauft. Du bist ein Meisterdieb! (+1 Win)"),
              "lose": (-250000, -100000, "Leider bist du beim Juwelier erwischt worden! Die Alarmanlage hat angeschlagen und die Polizei war schneller. (+1 Lose)")}),
            ("Farmer", {"win": (100000, 250000, "Du hast den Bauernhof erfolgreich ausgeraubt! Die Beute besteht aus wertvollen landwirtschaftlichen Geräten und Produkten. Gut gemacht! (+1 Win)"),
                "lose": (-100000, -100000, "Der Bauer hat dich erwischt und die Polizei gerufen! Du bist in der Klemme. (+1 Lose)")}),
            ("Gruppierung", {"win": (100000, 200000, "Du hast erfolgreich die Geheimgesellschaft infiltriert und wichtige Informationen gestohlen. Du bist ein Meister der Tarnung! (+1 Win)"),
                    "lose": (-100000, -100000, "Die Gruppierung hat deine Identität entdeckt und ist dir auf den Fersen! Du musst schnell verschwinden! (+1 Lose)")}),
            ("Bambi", {"win": (0, 0, "Du hast Bambi erfolgreich beklaut! Deine Skrupellosigkeit kennt keine Grenzen. (+1 Win)"),
            "lose": (0, 0, "Wie ehrlos! Wie konntest du es wagen, Bambi zu bestehlen? Schäme dich! (+1 Lose)")}),
            ("Museum", {"win": (50000, 100000, "Du hast ein wertvolles Kunstwerk aus dem Museum gestohlen und es für einen hohen Preis verkauft. Das ist ein großer Erfolg! (+1 Win)"),
                "lose": (-150000, -50000, "Die Alarmanlage wurde ausgelöst und du wurdest von den Sicherheitskräften des Museums erwischt. Das war ein riskanter Versuch! (+1 Lose)")}),
            ("Luxusvilla", {"win": (200000, 400000, "Du hast die Luxusvilla eines reichen Unternehmers erfolgreich ausgeraubt. Wertvolle Juwelen und Bargeld sind jetzt in deinem Besitz. (+1 Win)"),
                    "lose": (-300000, -150000, "Der Sicherheitsdienst der Luxusvilla hat dich erwischt! Sie waren besser vorbereitet als erwartet. (+1 Lose)")}),
            ("Kunstgalerie", {"win": (100000, 200000, "Du hast eine Kunstgalerie erfolgreich ausgeraubt und einige wertvolle Gemälde gestohlen. Jetzt musst du einen Käufer finden, der bereit ist, einen hohen Preis dafür zu zahlen. (+1 Win)"),
                    "lose": (-200000, -100000, "Die Polizei hat dich auf frischer Tat erwischt, als du versucht hast, aus der Kunstgalerie zu fliehen. Das war knapp! (+1 Lose)")})
        ]

        event, event_data = random.choice(events)
        outcome = random.choices(["win", "lose"], weights=[win_chance, 1 - win_chance])[0]
        payout = random.randint(event_data[outcome][0], event_data[outcome][1])
        event_text = event_data[outcome][2]

        await ctx.send(f"Du begehst Event: {event}... (Dauer: 1 Minute)")
        await asyncio.sleep(60)

        if outcome == "win":
            self.player_data[player_id]["win"] += 1
            self.player_data[player_id]["money"] += payout
            embed = discord.Embed(title=f"Ausgeraubt: {event}", color=discord.Color.gold())
            embed.add_field(name="Erbeuteter Betrag", value=f"{payout} Euro", inline=False)
            embed.description = event_text
            embed.set_footer(text=f"Dein neuer Kontostand: {self.player_data[player_id]['money']} Euro")
            await ctx.send(embed=embed)
        else:
            self.player_data[player_id]["lose"] += 1
            self.player_data[player_id]["money"] += payout
            embed = discord.Embed(title=f"Gescheitert: {event}", color=discord.Color.gold())
            embed.add_field(name="Verlust", value=f"{abs(payout)} Euro", inline=False)
            embed.description = event_text
            embed.set_footer(text=f"Dein neuer Kontostand: {self.player_data[player_id]['money']} Euro")
            await ctx.send(embed=embed)
    
        self.rob_cooldown[player_id] = time.time() + 1800

        self.save_data()  # Speichert die Spielerdaten

    @rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = error.retry_after
            hours, remainder = divmod(int(remaining_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"Du musst noch {hours} Stunden, {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")

        
    @commands.command()
    async def coinflip(self, ctx, bet: int):
        player_id = str(ctx.author.id)
        if player_id not in self.player_data:
            await ctx.send("Du hast noch keinen Account.")
            return

        if bet <= 0:
            await ctx.send("Der Einsatz muss größer als 0 sein.")
            return

        if self.player_data[player_id]["money"] < bet:
            await ctx.send("Du hast nicht genug Geld.")
            return

        outcomes = ["win", "lose"]
        outcome = random.choices(outcomes, weights=[0.50, 0.50], k=1)[0]  # Gleichgewichtige Gewinnchance

        if outcome == "win":
            winnings = bet * 2
            self.player_data[player_id]["money"] += winnings
            self.player_data[player_id]["win"] += 1
            self.save_data()
            await ctx.send(f"Du hast gewonnen! Du erhältst {winnings} Euro.")
        else:
            self.player_data[player_id]["money"] -= bet
            self.player_data[player_id]["lose"] += 1
            self.save_data()
            await ctx.send(f"Du hast verloren! Du verlierst {bet} Euro.")

    @commands.command()
    async def transferm(self, ctx, user: discord.Member, amount: int):
        sender_id = str(ctx.author.id)
        receiver_id = str(user.id)

        if sender_id not in self.player_data:
            await ctx.send("Du hast noch kein Spielerprofil. Erstelle ein Spielerprofil mit dem Befehl `!start`.")
            return

        if receiver_id not in self.player_data:
            await ctx.send("Der Empfänger hat noch kein Spielerprofil.")
            return

        sender_money = self.player_data[sender_id]["money"]

        if amount <= 0:
            await ctx.send("Der Betrag muss größer als 0 sein.")
            return

        if sender_money < amount:
            await ctx.send("Du hast nicht genug Geld, um diesen Betrag zu überweisen.")
            return

        self.player_data[sender_id]["money"] -= amount
        self.player_data[receiver_id]["money"] += amount
        self.save_data()
    
        await ctx.send(f"{ctx.author.mention} hat erfolgreich {amount} Euro an {user.mention} überwiesen.")

    @transferm.error
    async def transferm_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Bitte gib den Empfänger und den Betrag an. Beispiel: `!transferm @User [Betrag]`.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Der angegebene Benutzer wurde nicht gefunden.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Ungültiger Betrag. Bitte gib eine ganze Zahl an.")
    
    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def robuser(self, ctx, target: discord.Member):
        player_id = str(ctx.author.id)
        target_id = str(target.id)

        if player_id == target_id:
            await ctx.send("Du kannst dich nicht selbst überfallen.")
            return

        if player_id not in self.player_data:
            self.player_data[player_id] = {"money": 500000, "win": 0, "lose": 0, "last_daily": 0, "streak": 0}

        if target_id not in self.player_data:
            await ctx.send("Der angegebene Spieler hat noch keinen Täglichen Strike gesammelt.")
            return

        if player_id in self.robuser_cooldown:
            remaining_time = self.robuser_cooldown[player_id] - time.time()
            if remaining_time > 0:
                minutes, seconds = divmod(int(remaining_time), 60)
                await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")
                return

        player_money = self.player_data[player_id]["money"]
        target_money = self.player_data[target_id]["money"]
        win_chance = self.player_data[player_id].get("win_chance", 0.3)

        equipment_options = {
            "🔫": {"name": "Pistole und eine einfache Weste", "cost": 50000, "chance": 0.4},
            "🃏": {"name": "AR-15 Kit mit einer guten Rebellenweste", "cost": 100000, "chance": 0.5},
            "🧨": {"name": "7,62 MDR Kit und Kampfausrüstung", "cost": 200000, "chance": 0.6}
        }

        # Ausrüstungs-Nachricht senden und Reaktionen hinzufügen
        equipment_message = await ctx.send("Wähle eine Ausrüstung aus (oder reagiere mit ✅ für keinen Einsatz):")
        for emoji, equipment in equipment_options.items():
            await equipment_message.add_reaction(emoji)
            await ctx.send(f"{emoji} - {equipment['name']} (Kosten: {equipment['cost']})")
        await equipment_message.add_reaction("✅")

        def check(reaction, user):
            return user == ctx.author and (str(reaction.emoji) in equipment_options.keys() or str(reaction.emoji) == "✅") and reaction.message.id == equipment_message.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Du hast nicht innerhalb von 30 Sekunden reagiert. Der Überfall wurde abgebrochen.")
            return

        selected_equipment = equipment_options.get(str(reaction.emoji))
        if selected_equipment:
            equipment_name = selected_equipment["name"]
            equipment_cost = selected_equipment["cost"]
            win_chance = selected_equipment["chance"]
        else:
            equipment_name = "Keine Ausrüstung"
            equipment_cost = 0

        if player_money < equipment_cost:
            await ctx.send("Du hast nicht genug Geld, um diese Ausrüstung zu kaufen.")
            return

        max_steal_amount = int(target_money * 0.3)  # Maximal 30 % des Geldes des angegriffenen Spielers
        steal_amount = min(max_steal_amount, player_money)

        player_money -= steal_amount

        await ctx.send("Es wird nach Beute gesucht... (Dauer: 30 Sekunden)")
        await asyncio.sleep(30)

        outcome = random.choices(["win", "lose"], weights=[win_chance, 1 - win_chance])[0]
        if outcome == "win":
            max_payout = min(steal_amount, target_money)
            payout = random.randint(0, max_payout)
            player_money += payout
            target_money -= payout
        else:
            payout = min(player_money, 100000)  # Maximal den aktuellen Kontostand des Spielers
            player_money -= payout
            target_money += payout

        self.player_data[player_id]["money"] = player_money
        self.player_data[target_id]["money"] = target_money

        self.player_data[player_id]["win"] += 1 if outcome == "win" else 0
        self.player_data[player_id]["lose"] += 1 if outcome == "lose" else 0
        self.player_data[target_id]["win"] += 1 if outcome == "lose" else 0
        self.player_data[target_id]["lose"] += 1 if outcome == "win" else 0

        embed = discord.Embed(title="Überfallergebnis", color=discord.Color.gold())
        embed.add_field(name="Eingesetzte Ausrüstung", value=equipment_name, inline=False)
        if outcome == "win":
            embed.add_field(name="Erbeuteter Betrag", value=f"{payout} Euro", inline=False)
        else:
            embed.add_field(name="Verlorener Betrag", value=f"{payout} Euro", inline=False)
        if outcome == "win":
            embed.description = f"{ctx.author.mention} hat {target.mention} erfolgreich überfallen."
        else:
            embed.description = f"{ctx.author.mention} hat versucht, {target.mention} zu überfallen, aber es ist fehlgeschlagen."
        embed.set_footer(text=f"Dein neuer Kontostand: {player_money} Euro")
        await ctx.send(embed=embed)
        self.save_data()

    @robuser.error
    async def robuser_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = error.retry_after
            minutes, seconds = divmod(int(remaining_time), 60)
            await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")


    def save_data(self):
        with open('player_data.csv', 'w', newline='') as csvfile:
            fieldnames = ["player_id", "money", "win", "lose", "last_daily", "streak"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for player_id, data in self.player_data.items():
                writer.writerow({
                    "player_id": player_id,
                    "money": data["money"],
                    "win": data["win"],
                    "lose": data["lose"],
                    "last_daily": data["last_daily"],
                    "streak": data["streak"]
                })
    
    def load_data(self):
        try:
            with open('player_data.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    player_id = row["player_id"]
                    self.player_data[player_id] = {
                        "money": int(row["money"]),
                        "win": int(row["win"]),
                        "lose": int(row["lose"]),
                        "last_daily": float(row.get("last_daily", 0)),
                        "streak": int(row["streak"])
                    }
        except FileNotFoundError:
            pass
            
        self.save_data()

def setup(bot):
    bot.add_cog(commands_minigame(bot))