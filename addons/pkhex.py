import discord
import requests
import aiohttp
import io
import json
from datetime import datetime
from discord.ext import commands

class PKHeX(commands.Cog):

    """Handles all the PKHeX Related Commands. Does not load if coreconsole_server is not defined in config"""

    def __init__(self, bot):
        self.bot = bot
        try:
            r = requests.get(bot.coreconsole_server + "ping")  # Only lets module load if site sends back a 200 status code
        except requests.exceptions.MissingSchema:
            print("Error: coreconsole_server was not a valid url. Could not load pkhex.py")
        if not r.status_code == 200:
            print("Error: coreconsole_server was left blank in config.py, or the server is down. Commands in the PKHeX module cannot be used until this is rectified.")
        print('Addon "{}" loaded'.format(self.__class__.__name__))
        self.gens = [
            "red-blue",
            "silver",
            "ruby-sapphire",
            "diamond-pearl",
            "black-white",
            "x-y"
        ]

    @commands.command(hidden=True)
    async def ping_cc(self, ctx):
        """Pings the CoreConsole server"""
        if not ctx.author in (self.bot.creator, self.bot.allen):
            raise commands.errors.CheckFailure()
        msgtime = ctx.message.created_at.now()
        r = requests.get(self.bot.coreconsole_server + "ping")
        now = datetime.now()
        ping = now - msgtime
        await ctx.send("🏓 CoreConsole response time is {} milliseconds. Current CoreConsole status code is {}.".format(str(ping.microseconds / 1000.0), r.status_code))

    async def process_file(self, ctx, data, attachments, url):
        if not data and not attachments:
            await ctx.send("Error: No data was provided and no pkx file was attached.")
            return 400
        elif not data:
            atch = attachments[0]
            b = io.BytesIO()
            await atch.save(b)
            file = b.getvalue()
        else:
            try:
                async with aiohttp.ClientSession() as session:  # Stolen from https://stackoverflow.com/a/50236446 as I have no aiohttp knowledge
                    async with session.get(data) as resp:
                        file = io.BytesIO(await resp.read())
            except aiohttp.client_exceptions.InvalidURL:
                await ctx.send("The provided data was not valid.")
                return 400
        url = self.bot.coreconsole_server + url
        files = {'pkmn': file}
        r = requests.post(url=url, files=files)
        if r.status_code == 400:
            await ctx.send("The provided file was invalid.")
            return 400
        return r

    @commands.command(name='cl')
    async def check_legality(self, ctx, *, data=""):
        """Checks the legality of either a provided URL or attached pkx file. URL *must* be a direct download link"""
        ping = requests.get(self.bot.coreconsole_server + "ping")
        if not ping.status_code == 200:
            return await ctx.send("The CoreConsole server is currently down, and as such no commands in the PKHeX module can be used.")
        r = await self.process_file(ctx, data, ctx.message.attachments, "pkmn_info")
        if r == 400:
            return
        rj = r.json()
        reasons = rj["IllegalReasons"].split("\n")
        if reasons[0] == "Legal!":
            return await ctx.send("That Pokemon is legal!")
        embed = discord.Embed(title="Legality Issues", description="", colour=discord.Colour.red())
        for reason in reasons:
            values = reason.split(": ")
            values[0] = "**" + values[0] + "**: "
            val = ""
            for x in values[1:]:
                val += x + " "
            embed.description += values[0] + val
        await ctx.send(embed=embed)

    @commands.command(name='pi')
    async def poke_info(self, ctx, data=""):
        """Returns an embed with a Pokemon's nickname, species, and a few others. Takes a provided URL or attached pkx file. URL *must* be a direct download link"""
        ping = requests.get(self.bot.coreconsole_server + "ping")
        if not ping.status_code == 200:
            return await ctx.send("The CoreConsole server is currently down, and as such no commands in the PKHeX module can be used.")
        r = await self.process_file(ctx, data, ctx.message.attachments, "pkmn_info")
        if r == 400:
            return
        rj = r.json()
        embed = discord.Embed(title="Data for {}".format(rj["Nickname"]))
        embed.add_field(name="Species", value=rj["Species"])
        embed.add_field(name="Level", value=rj["Level"])
        embed.add_field(name="Nature", value=rj["Nature"])
        if int(rj["Generation"]) > 2:
            embed.add_field(name="Ability", value=rj["Ability"])
        embed.add_field(name="Original Trainer", value=rj["OT"])
        embed.add_field(name="Handling Trainer", value=rj["HT"])
        if int(rj["Generation"]) > 2:
            embed.add_field(name="Met Location", value=rj["MetLoc"])
            embed.add_field(name="Origin Game", value=rj["Version"])
        embed.add_field(name="Captured In", value=rj["Ball"])
        embed.add_field(name="EVs", value="**HP**: {}\n**Atk**: {}\n**Def**: {}\n**SpAtk**: {}\n**SpDef**: {}\n**Spd**: {}".format(rj["HP_EV"], rj["ATK_EV"], rj["DEF_EV"], rj["SPA_EV"], rj["SPD_EV"], rj["SPE_EV"]))
        embed.add_field(name="IVs", value="**HP**: {}\n**Atk**: {}\n**Def**: {}\n**SpAtk**: {}\n**SpDef**: {}\n**Spd**: {}".format(rj["HP_IV"], rj["ATK_IV"], rj["DEF_IV"], rj["SPA_IV"], rj["SPD_IV"], rj["SPE_IV"]))
        embed.add_field(name="Moves", value="**1**: {}\n**2**: {}\n**3**: {}\n**4**: {}".format(rj["Move1"], rj["Move2"], rj["Move3"], rj["Move4"]))
        print(int(rj["Generation"]))
        used_gen = self.gens[int(rj["Generation"])-1] if int(rj["Generation"]) < 7 else "x-y"
        sprite = "https://sprites.flagbrew.org/{}/{}/{}.png".format(used_gen, "shiny" if rj["IsShiny"] else "normal", rj["Species"].lower())
        embed.set_thumbnail(url=sprite)
        embed.colour = discord.Colour.green() if rj["IllegalReasons"] == "Legal!" else discord.Colour.red()
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            return await ctx.send("There was an error showing the data for this pokemon. {}, {}, or {} please check this out!\n{} please do not delete the file. Exception below.\n\n```{}```".format(self.bot.creator.mention, self.bot.pie.mention, self.bot.allen.mention, ctx.author.mention, e))

    @commands.command(name='gq')
    async def gen_pkmn_qr(self, ctx, data=""):
        """Gens a QR code that PKSM can read. Takes a provided URL or attached pkx file. URL *must* be a direct download link"""
        ping = requests.get(self.bot.coreconsole_server + "ping")
        if not ping.status_code == 200:
            return await ctx.send("The CoreConsole server is currently down, and as such no commands in the PKHeX module can be used.")
        r = await self.process_file(ctx, data, ctx.message.attachments, "pkmn_qr")
        if r == 400:
            return
        qr = discord.File(io.BytesIO(r.content), 'pokemon_qr.png')
        d = (await self.process_file(ctx, data, ctx.message.attachments, "pkmn_info")).json()
        await ctx.send("QR containing a {} for Generation {}".format(d["Species"], d["Generation"]), file=qr)

    @commands.command(name='cm')
    async def check_moves(self, ctx, *, input_data):
        """Checks if a given pokemon can learn moves. Separate moves using pipes. Example: .cm pikachu | quick attack | hail"""
        ping = requests.get(self.bot.coreconsole_server + "ping")
        if not ping.status_code == 200:
            return await ctx.send("The CoreConsole server is currently down, and as such no commands in the PKHeX module can be used.")
        input_data = input_data.replace("| ", "|").replace(" |", "|").replace(" | ", "|")
        input_data = input_data.split("|")
        pokemon = input_data[0]
        moves = input_data[1:]
        if not moves:
            return await ctx.send("No moves provided, or the data provided was in an incorrect format.\n```Example: .cm pikachu | quick attack | hail```")
        data = {
            "query": pokemon + "|" + "|".join(moves)
        }
        r = requests.post(self.bot.coreconsole_server + "query/move_learn", data=data)
        if r.status_code == 400:
            return await ctx.send("Something you sent was invalid. Please double check your data and try again.")
        rj = r.json()
        embed = discord.Embed(title="Move Lookup for {}".format(pokemon.title()), description="")
        for move in rj:
            embed.description += "**{}** is {} learnable.\n".format(move["MoveName"].title(), "not" if not move["Learnable"] else "")
        await ctx.send(embed=embed)

    @commands.command(name='ce')
    async def check_encounters(self, ctx, generation: int, *, input_data):
        """Outputs the locations a given pokemon can be found. Separate data using pipes. Example: .cm 6 pikachu | volt tackle"""
        ping = requests.get(self.bot.coreconsole_server + "ping")
        if not ping.status_code == 200:
            return await ctx.send("The CoreConsole server is currently down, and as such no commands in the PKHeX module can be used.")
        input_data = input_data.replace("| ", "|").replace(" |", "|").replace(" | ", "|")
        input_data = input_data.split("|")
        pokemon = input_data[0]
        moves = input_data[1:]
        data = {
            "query": pokemon + "|" + "|".join(moves)
        }
        r = requests.post(self.bot.coreconsole_server + "query/encounter", data=data)
        rj = r.json()
        embed = discord.Embed(title="Encounter Data for {} in Generation {}{}{}".format(pokemon.title(), generation, " with move(s) " if len(moves) > 0 else "", ", ".join([move.title() for move in moves])))
        generation_data = rj["Gen{}".format(generation)]
        for encs in generation_data:
            locations = {}
            for loc in encs["Locations"]:
                if loc["Location"] == "":
                    locations[", ".join(loc["Games"])] = "N/A"
                    continue
                locations[", ".join(loc["Games"])] = loc["Location"]
            field_values = ""
            for location in locations:
                field_values += "{} in **{}**.\n".format(location, locations[location])
            embed.add_field(name="As {}".format(encs["EncounterType"]), value=field_values, inline=False)
        if len(embed.fields) == 0:
            return await ctx.send("Could not find matching encounter data for {} in Generation {}{}{}.".format(pokemon.title(), generation, " with move(s) " if len(moves) > 0 else "", ", ".join([move.title() for move in moves])))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(PKHeX(bot))