#!/usr/bin/env python3

import json, requests
import discord
from discord.ext import commands

desc = "You can get the latest release of {}."
desc_pksm = "PKSM [here](https://github.com/BernardoGiordano/PKSM/releases/latest)"
desc_checkpoint = "Checkpoint [here](https://github.com/BernardoGiordano/Checkpoint/releases/latest)"
desc_pickr = "Pickr3DS [here](https://github.com/BernardoGiordano/Pickr3DS/releases/latest)"
desc_tools = "PKSM-Tools [here](https://github.com/BernardoGiordano/PKSM-Tools/releases)"
desc_qraken = "QRaken [here](https://github.com/BernardoGiordano/QRaken/releases/latest)"
desc_sharkive = "Sharkive [here](https://github.com/BernardoGiordano/Sharkive/releases/latest)"

class Info:

    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
        
        
    @commands.command(aliases=['releases', 'latest']) # QR Codes commented out until a new source for the files is provided
    async def release(self, ctx, app = ""):
        """Returns the latest release for Bernardo's projects"""
        if app.lower() == "pksm" or ctx.invoked_with == "latest":
            embed = discord.Embed(description=desc.format(desc_pksm))
            releases = requests.get("https://api.github.com/repos/BernardoGiordano/PKSM/releases").json()
            for asset in releases[0]['assets']:
                if asset['name'] == "PKSM.cia":
                    embed.set_image(url="https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=" + asset['browser_download_url'] + "&choe=UTF-8.png")
        elif app.lower() == "checkpoint":
            embed = discord.Embed(description=desc.format(desc_checkpoint))
            releases = requests.get("https://api.github.com/repos/BernardoGiordano/Checkpoint/releases").json()
            for asset in releases[0]['assets']:
                if asset['name'] == "Checkpoint.cia":
                    embed.set_image(url="https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=" + asset['browser_download_url'] + "&choe=UTF-8.png")
        elif app.lower() == "pickr":
            embed = discord.Embed(description=desc.format(desc_pickr))
            releases = requests.get("https://api.github.com/repos/BernardoGiordano/Pickr3DS/releases").json()
            for asset in releases[0]['assets']:
                if asset['name'] == "Pickr3DS.cia":
                    embed.set_image(url="https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=" + asset['browser_download_url'] + "&choe=UTF-8.png")
        elif app.lower() == "sharkive":
            embed = discord.Embed(description=desc.format(desc_sharkive))
            releases = requests.get("https://api.github.com/repos/BernardoGiordano/Sharkive/releases").json()
            for asset in releases[0]['assets']:
                if asset['name'] == "Sharkive.cia":
                    embed.set_image(url="https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=" + asset['browser_download_url'] + "&choe=UTF-8.png")
        elif app.lower() == "pksm-tools" or app.lower() == "tools":
            embed = discord.Embed(description=desc.format(desc_tools))
        elif app.lower() == "qraken":
            embed = discord.Embed(description=desc.format(desc_qraken))
        else:
            embed = discord.Embed(description=desc.format(desc_pksm) + "\n" + desc.format(desc_checkpoint) + "\n" + desc.format(desc_tools) + "\n" + desc.format(desc_pickr) + "\n" + desc.format(desc_qraken))
        await ctx.send(embed=embed)
        
    @commands.command()
    async def about(self, ctx):
        """Information about the bot"""
        await ctx.send("This is a bot coded in python for use in the PKSM server, made by {}#{}. You can view the source code here: <https://github.com/GriffinG1/PKSMBot>.".format(self.bot.creator.name, self.bot.creator.discriminator))    
    @commands.command()
    async def readme(self, ctx, app = ""):
        """Here are the readmes you should read
        Available readmes: PKSM, PKSMScript (or scripts), serveLegality (or legality), servepkx, Sharkive"""
        if app.lower() == "scripts" or app.lower() == "pksmscript":
            embed = discord.Embed(description="You can read about PKSM scripts [here](https://github.com/BernardoGiordano/PKSM-Tools/blob/master/PKSMScript/README.md).")
        elif app.lower() == "servelegality" or app.lower() == "legality":
            embed = discord.Embed(description="You can read serveLegality's readme [here](https://github.com/BernardoGiordano/PKSM-Tools/blob/master/serveLegality/README.md).")
        elif app.lower() == 'servepkx' or app.lower() == 'servepkx-browser':
            embed = discord.Embed(description="You can read servepkx's readme [here](https://github.com/BernardoGiordano/PKSM-Tools/blob/master/servepkx/servepkx-browser/README.md).")
        elif app.lower() == 'servepkx-go':
            embed = discord.Embed(description="You can read servepkx-go's readme [here](https://github.com/BernardoGiordano/PKSM-Tools/blob/master/servepkx/servepkx-go/README.md).")
        elif app.lower() == 'servepkx-gui' or app.lower() == 'servepkx-java':
            embed = discord.Embed(description="You can read servepkx-gui's readme [here](https://github.com/BernardoGiordano/PKSM-Tools/blob/master/servepkx/servepkx-gui/README.md).")
        elif app.lower() == "sharkive":
            embed = discord.Embed(description="You can read Sharkive's readme [here](https://github.com/BernardoGiordano/Sharkive/blob/master/README.md).")
        else:
            embed = discord.Embed(description="You can read PKSM's readme [here](https://github.com/BernardoGiordano/PKSM/blob/master/README.md).")
        await ctx.send(embed=embed)
		
    @commands.command()
    async def storage(self, ctx):
        """Storage from 5.0.0+"""
        await ctx.send("If you can't see your storage correctly anymore, make sure you read what changed here: https://github.com/BernardoGiordano/PKSM#storage-changes-from-500")
        
    @commands.command(aliases=['patron'])
    async def patreon(self, ctx):
        """Donate here"""
        await ctx.send("You can donate to Bernardo on Patreon here: <https://www.patreon.com/bernardogiordano>.")
        
    @commands.command()
    async def faq(self, ctx):
        """Frequently Asked Questions"""
        embed = discord.Embed(title="Frequently Asked Questions")
        embed.add_field(name="When will Virtual Console games be supported?", value="Never.")
        embed.add_field(name="Are flashcards supported? If not, when will support for them be added?", value="Flashcards are not supported and never will be.")
        embed.add_field(name="When will support for Storage and Editor be added for DS games?", value="Currently never, unless someone decides to make a contribution and develop it.")
        embed.add_field(name="When will support be added for editing your backpack and items?", value="Limited editing is possible with scripts. Full editing won't be possible unless someone decides to make a contribution and develop it.")
        embed.add_field(name="Why do I have to wait so long for new releases?", value="A) because you think you're entitled to everything. B) PKSM is currently being rewritten and as such no new releases will be coming until that is finished.")
        await ctx.send(embed=embed)

    @commands.command()
    async def date(self, ctx):
        """How to Change PKSM's Default Met Date"""
        embed = discord.Embed(title="How to Change PKSM's Default Met Date")
        embed.description = ("1. Select your game\n"
                             "2. Select options\n"
                             "3. Move your cursor to the byte you want to change.\n"
                             "\t\t\u2022 0x22 is the day, 0x23 is the month, and 0x24 is the year.\n"
                             "\t\t\u2022 Keep in mind that all numbers are hexadecimals.\n"
                             "4. Tap the plus button to increase the value of those bytes and minus to decrease.\n"
                             "5. Once you've made your changes, press B to exit")
        await ctx.send(embed=embed)
	
        
    @commands.command(aliases=['qr', 'qrcodes'])
    async def qrcode(self, ctx):
        """REEE WHY CANT I GET MY QR CODES AHH"""
        embed = discord.Embed(title="What Happened to the QR Codes?")
        embed.description = "Due to changes in how [GitHub](https://www.reddit.com/r/3dshacks/comments/7zof0c/reminder_github_has_dropped_tlsv111_support_as_of/) works, QR codes can no longer be scanned using FBI. You can use [QRaken](https://github.com/BernardoGiordano/QRaken/releases) to download apps using QR codes."
        await ctx.send(embed=embed)
        
    @commands.command()
    async def titledb(self, ctx):
        """Why you shouldn't download from TitleDB"""
        await ctx.send("TitleDB is in no way condoned by Bernardo for downloading any of his projects. Please download them from official sources, such as his GitHub.")
        
    @commands.command()
    async def fbi(self, ctx):
        """This is not an FBI support server!!!!!"""
        await ctx.send("This server is not meant for FBI troubleshooting, nor is Bernardo a developer of FBI. If you have issues scanning QR codes with FBI, that's an FBI issue. **Don't ask for help with it here.**")
        
    @commands.command() # Taken from https://github.com/nh-server/Kurisu/blob/master/addons/assistance.py#L198-L205
    async def vguides(self, ctx):
        """Information about video guides relating to custom firmware"""
        embed = discord.Embed(title="Why you shouldn't use video guides")
        embed.description = ('"Video guides" are not recommended for use. Their contents generally become outdated very quickly for them to be of any use, and they are harder to update unlike a written guide.\n\n'
                            'When this happens, video guides become more complicated than current methods, having users do certain tasks which may not be required anymore.\n\n'
                            'There is also a risk of the uploader spreading misinformation or including potentially harmful files, sometimes unintentionally.')
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Info(bot))
