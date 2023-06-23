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
        self.player_data = {}
        self.lottery_data = {}
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
                "lose": 0,
                "streak": 0
            }

        if player_id in self.daily_cooldown:
            remaining_time = self.daily_cooldown[player_id] - time.time()
            if remaining_time > 0:
                minutes, seconds = divmod(int(remaining_time), 60)
                await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")
                return

        streak = self.player_data[player_id].get("streak", 0)
        payout = 50000 * (streak + 1)  # Calculate payout based on streak
        self.player_data[player_id]["money"] += payout
        self.player_data[player_id]["streak"] = (streak + 1) % 11  # Increase streak, reset to 0 after 10 days
        self.save_data()

        embed = discord.Embed(title="Tägliche Auszahlung", color=0xFFD700)
        embed.add_field(name="Betrag", value=f"{payout} Euro", inline=False)
        embed.add_field(name="Streak", value=f"{streak + 1} Tage", inline=False)
        embed.set_footer(text=f"Dein neuer Kontostand: {self.player_data[player_id]['money']} Euro")
        await ctx.send(embed=embed)

        self.daily_cooldown[player_id] = time.time() + 86400

    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = error.retry_after
            minutes, seconds = divmod(int(remaining_time), 60)
            await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")
        else:
            raise error
            
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
            self.player_data[player_id] = {"money": 500000, "win": 0, "lose": 0}

        if player_id in self.rob_cooldown:
            remaining_time = self.rob_cooldown[player_id] - time.time()
            if remaining_time > 0:
                minutes, seconds = divmod(int(remaining_time), 60)
                await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")
                return

        confirmation_message = await ctx.send("Möchtest du einen Raubzug starten? Reagiere mit ✅, um zu bestätigen. (Kostet 100K)")
        await confirmation_message.add_reaction("✅")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == confirmation_message.id

        try:
            await self.bot.wait_for("reaction_add", timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Du hast nicht innerhalb von 30 Sekunden reagiert. Der Raubzug wurde abgebrochen.")
            return

        self.player_data[player_id]["money"] -= 100000

        await ctx.send("Es wird nach Beute gesucht... (Dauer: 30 Sekunden)")
        await asyncio.sleep(30)

        events = [
            ("Zentralbank", {"win": (250000, 500000, "Du hast den ultimativen Raubzug hingelegt und bewiesen, dass du ein Meisterdieb bist. (+1 Win)"),
                    "lose": (-500000, -100000, "Oh nein, du wurdest von der Polizei erwischt! Vielleicht warst du nicht schnell genug oder hast nicht vorsichtig genug gehandelt oder du bist einfach nur schlecht! (+1 Lose)")}),
            ("Bankfiliale", {"win": (100000, 250000, "Herzlichen Glückwunsch! Du hast es geschafft, die Bankfiliale erfolgreich auszurauben. Jetzt musst du schnell entkommen, bevor die Polizei dich erwischt. Hüte dich vor den Kameras und den Sicherheitsleuten, die dich aufspüren könnten. Aber pass auf, denn es wird nicht einfach sein, den ganzen Weg zurückzulegen und das gestohlene Geld zu behalten. (+1 Win)"),
                    "lose": (-250000, -100000, "Die Polizei hat dich nach einer wilden Verfolgungsjagd erwischt! Du solltest schneller sein oder bessere Fluchtstrategien entwickeln. (+1 Lose)")}),
            ("Juwelier", {"win": (100000, 250000, "Glückwunsch! Du hast erfolgreich den Juwelier ausgeraubt und die wertvollen Diamanten verkauft. Du bist ein Meisterdieb! (+1 Win)"),
              "lose": (-250000, -100000, "Leider bist du beim Juwelier erwischt worden! Die Alarmanlage hat angeschlagen und die Polizei war schneller. (+1 Lose)")}),
            ("Farmer", {"win": (100000, 250000, "Du hast den Bauernhof erfolgreich ausgeraubt! Die Beute besteht aus wertvollen landwirtschaftlichen Geräten und Produkten. Gut gemacht! (+1 Win)"),
                "lose": (-100000, -100000, "Der Bauer hat dich erwischt und die Polizei gerufen! Du bist in der Klemme. (+1 Lose)")}),
            ("Gruppierung", {"win": (0, 0, "Du hast erfolgreich die Geheimgesellschaft infiltriert und wichtige Informationen gestohlen. Du bist ein Meister der Tarnung! (+1 Win)"),
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
        outcome = random.choice(["win", "lose"])
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
            minutes, seconds = divmod(int(remaining_time), 60)
            await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")
        
    @commands.command()
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def rob(self, ctx):
        player_id = str(ctx.author.id)
        if player_id not in self.player_data:
            self.player_data[player_id] = {"money": 500000, "win": 0, "lose": 0}

        if player_id in self.rob_cooldown:
            remaining_time = self.rob_cooldown[player_id] - time.time()
            if remaining_time > 0:
                minutes, seconds = divmod(int(remaining_time), 60)
                await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")
                return

        confirmation_message = await ctx.send("Möchtest du einen Raubzug starten? Reagiere mit ✅, um zu bestätigen. (Kostet 100K)")
        await confirmation_message.add_reaction("✅")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == confirmation_message.id

        try:
            await self.bot.wait_for("reaction_add", timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Du hast nicht innerhalb von 30 Sekunden reagiert. Der Raubzug wurde abgebrochen.")
            return

        self.player_data[player_id]["money"] -= 100000

        await ctx.send("Es wird nach Beute gesucht... (Dauer: 30 Sekunden)")

        # Gif für den Raubzug
        rob_gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTkxNWU5OTU5YjAyMTZiYzE0NDFhYzc5MmE0MzZiMTY4MDUxODBkYyZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/l3vR3OeImw8fD80Mg/giphy.gif"
        win_gif_url = "https://media.giphy.com/media/JpG2A9P3dPHXaTYrwu/giphy.gif"
        lose_gif_url = "https://media.giphy.com/media/Ti3g0f4Sy90Xc1Lf5y/giphy.gif"

        embed = discord.Embed(title="Raubzug", description="Es wird nach Beute gesucht...", color=discord.Color.dark_gold())
        embed.set_image(url=rob_gif_url)
        progress_message = await ctx.send(embed=embed)

        await asyncio.sleep(30)

        events = [
            ("Zentralbank", {"win": (250000, 500000, "Du hast den ultimativen Raubzug hingelegt und bewiesen, dass du ein Meisterdieb bist. (+1 Win)"),
                    "lose": (-500000, -100000, "Oh nein, du wurdest von der Polizei erwischt! Vielleicht warst du nicht schnell genug oder hast nicht vorsichtig genug gehandelt oder du bist einfach nur schlecht! (+1 Lose)")}),
            ("Bankfiliale", {"win": (100000, 250000, "Herzlichen Glückwunsch! Du hast es geschafft, die Bankfiliale erfolgreich auszurauben. Jetzt musst du schnell entkommen, bevor die Polizei dich erwischt. Hüte dich vor den Kameras und den Sicherheitsleuten, die dich aufspüren könnten. Aber pass auf, denn es wird nicht einfach sein, den ganzen Weg zurückzulegen und das gestohlene Geld zu behalten. (+1 Win)"),
                    "lose": (-250000, -100000, "Die Polizei hat dich nach einer wilden Verfolgungsjagd erwischt! Du solltest schneller sein oder bessere Fluchtstrategien entwickeln. (+1 Lose)")}),
            ("Juwelier", {"win": (100000, 250000, "Glückwunsch! Du hast erfolgreich den Juwelier ausgeraubt und die wertvollen Diamanten verkauft. Du bist ein Meisterdieb! (+1 Win)"),
              "lose": (-250000, -100000, "Leider bist du beim Juwelier erwischt worden! Die Alarmanlage hat angeschlagen und die Polizei war schneller. (+1 Lose)")}),
            ("Farmer", {"win": (100000, 250000, "Du hast den Bauernhof erfolgreich ausgeraubt! Die Beute besteht aus wertvollen landwirtschaftlichen Geräten und Produkten. Gut gemacht! (+1 Win)"),
                "lose": (-100000, -100000, "Der Bauer hat dich erwischt und die Polizei gerufen! Du bist in der Klemme. (+1 Lose)")}),
            ("Gruppierung", {"win": (0, 0, "Du hast erfolgreich die Geheimgesellschaft infiltriert und wichtige Informationen gestohlen. Du bist ein Meister der Tarnung! (+1 Win)"),
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
        outcome = random.choice(["win", "lose"])
        payout = random.randint(event_data[outcome][0], event_data[outcome][1])
        event_text = event_data[outcome][2]

        if outcome == "win":
            self.player_data[player_id]["win"] += 1
            self.player_data[player_id]["money"] += payout
            embed = discord.Embed(title=f"Ausgeraubt: {event}", color=discord.Color.gold())
            embed.add_field(name="Erbeuteter Betrag", value=f"{payout} Euro", inline=False)
            embed.description = event_text
            embed.set_image(url=win_gif_url)
            embed.set_footer(text=f"Dein neuer Kontostand: {self.player_data[player_id]['money']} Euro")
        else:
            self.player_data[player_id]["lose"] += 1
            self.player_data[player_id]["money"] += payout
            embed = discord.Embed(title=f"Gescheitert: {event}", color=discord.Color.red())
            embed.add_field(name="Verlust", value=f"{abs(payout)} Euro", inline=False)
            embed.description = event_text
            embed.set_image(url=lose_gif_url)
            embed.set_footer(text=f"Dein neuer Kontostand: {self.player_data[player_id]['money']} Euro")

        await progress_message.edit(embed=embed)

        self.rob_cooldown[player_id] = time.time() + 1800

        self.save_data()  # Speichert die Spielerdaten

    @rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = error.retry_after
            minutes, seconds = divmod(int(remaining_time), 60)
            await ctx.send(f"Du musst noch {minutes} Minuten und {seconds} Sekunden warten, bevor du das wieder tun kannst.")            
        
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
    async def lotto(self, ctx, numbers: commands.Greedy[int]):
        player_id = str(ctx.author.id)
        if len(numbers) != 6:
            await ctx.send("Du musst genau 6 Zahlen angeben.")
            await ctx.send("Die Zahlen müssen zwischen 1 und 49 liegen.")
            return

        if any(num <= 0 or num > 49 for num in numbers):
            await ctx.send("Die Zahlen müssen zwischen 1 und 49 liegen.")
            return

        if player_id not in self.player_data:
            self.player_data[player_id] = {"money": 500000, "win": 0, "lose": 0}

        ticket_cost = 25000
        if self.player_data[player_id]["money"] < ticket_cost:
            await ctx.send("Du hast nicht genug Geld, um ein Lotto-Ticket zu kaufen.")
            return

        self.player_data[player_id]["money"] -= ticket_cost
        self.save_data()

        self.lottery_data[player_id] = {"numbers": numbers, "ticket_cost": ticket_cost}
        self.save_lottery_data()

        await ctx.send(f"Du hast an der Lotterie teilgenommen. Viel Glück!")

    @commands.command()
    async def ergebnis(self, ctx):
        player_id = str(ctx.author.id)
        if player_id not in self.lottery_data:
            await ctx.send("Du hast noch nicht an der aktuellen Lotterie teilgenommen.")
            return

        drawn_numbers = random.sample(range(1, 50), 6)
        matching_numbers = set(self.lottery_data[player_id]["numbers"]) & set(drawn_numbers)
        num_matching = len(matching_numbers)

        ticket_cost = self.lottery_data[player_id]["ticket_cost"]

        del self.lottery_data[player_id]
        self.save_lottery_data()

        if num_matching == 6:
            jackpot_amount = self.jackpot_data.get("amount", 0)
            self.jackpot_data["amount"] = 0
            self.save_jackpot_data()
            self.player_data[player_id]["money"] += jackpot_amount
            self.player_data[player_id]["win"] += 1
            self.save_data()
            await ctx.send(f"Glückwunsch! Du hast alle 6 Zahlen richtig erraten und den Jackpot in Höhe von {jackpot_amount} gewonnen!")
        elif num_matching >= 3:
            prize = ticket_cost * 5
            self.player_data[player_id]["money"] += prize
            self.player_data[player_id]["win"] += 1
            self.save_data()
            await ctx.send(f"Glückwunsch! Du hast {num_matching} Zahlen richtig erraten und gewinnst {prize}!")
        else:
            self.player_data[player_id]["lose"] += 1
            self.save_data()
            await ctx.send(f"Leider hast du keine ausreichende Anzahl an Zahlen richtig erraten. Versuche es erneut!")

    @commands.command()
    async def jackpot(self, ctx):
        jackpot_amount = self.jackpot_data.get("amount", 0)
        await ctx.send(f"Aktueller Jackpot: {jackpot_amount}")

    def save_data(self):
        with open('player_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["player_id", "money", "win", "lose"])
            for player_id, data in self.player_data.items():
                writer.writerow([player_id, data["money"], data["win"], data["lose"]])

    def save_data(self):
        with open('player_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["player_id", "money", "win", "lose"])
            for player_id, data in self.player_data.items():
                writer.writerow([player_id, data["money"], data["win"], data["lose"]])

    def save_jackpot_data(self):
        with open('jackpot_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["amount"])
            writer.writerow([self.jackpot_data.get("amount", 0)])
    
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
        
    def load_jackpot_data(self):
        try:
            with open('jackpot_data.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.jackpot_data["amount"] = int(row["amount"])
        except FileNotFoundError:
            pass

        self.save_jackpot_data()

    def save_lottery_data(self):
        with open('lottery_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["player_id", "numbers", "ticket_cost"])
            for player_id, data in self.lottery_data.items():
                writer.writerow([player_id, " ".join(str(num) for num in data["numbers"]), data["ticket_cost"]])

    def load_lottery_data(self):
        try:
            with open('lottery_data.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.lottery_data[row["player_id"]] = {
                        "numbers": [int(num) for num in row["numbers"].split()],
                        "ticket_cost": int(row["ticket_cost"])
                    }
        except FileNotFoundError:
            pass

        self.save_lottery_data()

    async def lottery_draw(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = time.localtime()
            if now.tm_hour == 0 and now.tm_min == 0:
                self.draw_lottery()
            await asyncio.sleep(60)

    def draw_lottery(self):
        drawn_numbers = random.sample(range(1, 50), 6)
        winners = []
        for player_id, data in self.lottery_data.items():
            matching_numbers = set(data["numbers"]) & set(drawn_numbers)
            num_matching = len(matching_numbers)
            if num_matching >= 3:
                winners.append((player_id, num_matching))
        
        if winners:
            total_winners = len(winners)
            prize_per_winner = self.jackpot_data.get("amount", 0) // total_winners
            for winner_id, num_matching in winners:
                self.player_data[winner_id]["money"] += prize_per_winner
                self.player_data[winner_id]["win"] += 1
            self.save_data()
        
        self.lottery_data.clear()
        self.save_lottery_data()

        self.jackpot_data["amount"] = 0
        self.save_jackpot_data()

        drawn_numbers_str = ", ".join(str(num) for num in drawn_numbers)
        self.bot.get_channel(1107669878124589066).send(f"Die Lotterie-Ziehung ist erfolgt! Die gezogenen Zahlen sind: {drawn_numbers_str}")
        
        if winners:
            winner_list = "\n".join(f"<@{winner_id}> - {num_matching} Richtige" for winner_id, num_matching in winners)
            self.bot.get_channel(1107669878124589066).send(f"Herzlichen Glückwunsch an die Gewinner:\n{winner_list}")

    def start_lottery_draw_task(self):
        self.bot.loop.create_task(self.lottery_draw())

def setup(bot):
    bot.add_cog(commands_minigame(bot))