import discord
import requests
import aiohttp
import io
import json
from discord.ext import commands

"""Handles all the PKHeX Related Commands. Does not load if coreconsole_server is not defined in config"""

class PKHeX(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        try:
            r = requests.get(bot.coreconsole_server + "ping")  # Only lets cog load if site sends back a 200 status code
        except requests.exceptions.MissingSchema:
            print("Error: coreconsole_server was not a valid url. Could not load pkhex.py")
        if not r.status_code == 200:
            print("Error: coreconsole_server was left blank in config.py. Could not load pkhex.py")
            raise(MissingServerLink)
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    @commands.command(name="cl")
    async def check_legality(self, ctx, *, data=""):
        """Checks the legality of either a provided url or attached pkx file. URL *must* be a direct download link"""
        if not data and not ctx.message.attachments:
            return await ctx.send("Error: No data was provided and no pkx file was attached.")
        elif not data:
            atch = ctx.message.attachments[0]
            b = io.BytesIO()
            await atch.save(b)
            file = b.getvalue()
        else:
            async with aiohttp.ClientSession() as session:  # Stolen from https://stackoverflow.com/a/50236446 as I have no aiohttp knowledge
                async with session.get(data) as resp:
                    file = io.BytesIO(await resp.read())
        url = self.bot.coreconsole_server + "pkmn_info"
        files = {'pkmn': file}
        r = requests.post(url=url, files=files)
        if r.status_code == 400:
            return await ctx.send("The provided file was invalid. Please try again later.")
        rj = r.json()
        reasons = rj["IllegalReasons"].split("\n")
        if reasons[0] == "Legal!":
            return await ctx.send("That Pokemon is legal!")
        embed = discord.Embed(title="Legality Issues", description="")
        for reason in reasons:
            values = reason.split(": ")
            values[0] = "**" + values[0] + "**: "
            val = ""
            for x in values[1:]:
                val += x + " "
            embed.description += values[0] + val
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(PKHeX(bot))

class MissingServerLink(commands.UserInputError):
    pass