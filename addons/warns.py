import discord
import json
import random
import io
from datetime import datetime
from discord.ext import commands
from addons.helper import restricted_to_bot


class Warning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if self.bot.is_mongodb:
            self.db = bot.db
        print(f'Addon "{self.__class__.__name__}" loaded')

    @commands.command()
    @commands.has_any_role("Discord Moderator", "FlagBrew Team")
    async def warn(self, ctx, target: discord.Member, *, reason="No reason was given"):
        """Warns a user. Kicks at 3 and 4 warnings, bans at 5"""
        has_attch = bool(ctx.message.attachments)
        try:
            self.bot.warns_dict[str(target.id)]
        except KeyError:
            self.bot.warns_dict[str(target.id)] = []
        self.bot.warns_dict[str(target.id)].append(
            {
                "reason": reason,
                "date": datetime.now().strftime("%D %H:%M:%S"),  # trying to decide if I want to change this to a discord aware timestamp. don't want to have to update the old values or support though
                "warned_by": f"{ctx.author}",
            })
        warns = self.bot.warns_dict[str(target.id)]
        dm_msg = f"You were warned on {ctx.guild}.\nThe reason provided was: `{reason}`.\nThis is warn #{len(warns)}."
        log_msg = ""
        if len(warns) >= 5:
            dm_msg += "\nYou were banned for this warn. If you believe this was in error, please contact FlagBrew via email at `flagbrewinfo@gmail.com`."
            log_msg += "They were banned as a result of this warn."
        elif len(warns) >= 3:
            dm_msg += "\nYou were kicked for this warn. If you would like to rejoin the server, here is a permanent invite: https://discord.gg/95U8FEKZFZ."
            if len(warns) == 4:
                dm_msg += "\nYou will be automatically banned if you are warned again."
            log_msg += "They were kicked as a result of this warn."
        elif len(warns) == 2:
            dm_msg += "You will be automatically kicked if you are warned again."
        embed = discord.Embed(title=f"{target} warned")
        embed.description = f"{target} | {target.id} was warned in {ctx.channel.mention} by {ctx.author} for `{reason}`. This is warn #{len(warns)}. {log_msg}"
        dm_msg += "\n\nPlease direct any possible complaints to <@958140281633513563>. DMing Staff or Team members to complain will be met with further moderator action, as per rule 6."
        try:
            if has_attch:
                img_bytes = await ctx.message.attachments[0].read()
                warn_img = discord.File(io.BytesIO(img_bytes), 'image.png')
                log_img = discord.File(io.BytesIO(img_bytes), 'warn_image.png')
                await target.send(dm_msg, file=warn_img)
            else:
                await target.send(dm_msg)
        except discord.Forbidden:
            embed.description += "\n**Could not DM user.**"
        if self.bot.is_mongodb:
            self.db['warns'].update_one(
                {
                    "user": str(target.id)
                },
                {
                    "$set": {
                        "user": str(target.id),
                        "warns": self.bot.warns_dict[str(target.id)]
                    }
                }, upsert=True)
        with open("saves/warns.json", "w") as file:
            json.dump(self.bot.warns_dict, file, indent=4)
        if len(warns) >= 5:
            embed = discord.Embed()
            img_choice = random.randint(1, 26)
            if img_choice in range(1, 13):  # ampharos
                embed.set_image(url="https://cdn.sigkill.tech/misc/ampharos-banned.jpg")
            if img_choice in range(13, 25):  # eevee
                embed.set_image(url="https://cdn.sigkill.tech/misc/eevee-banned.png")
            if img_choice in range(25, 27):  # giratina
                embed.set_image(url="https://cdn.sigkill.tech/misc/giratina-banned.png")
            await target.ban(reason=f"Warn #{len(warns)}", delete_message_days=0)
        elif len(warns) >= 3:
            await target.kick(reason=f"Warn #{len(warns)}")
        try:
            if has_attch:
                embed.set_thumbnail(url="attachment://warn_image.png")
                await self.bot.logs_channel.send(embed=embed, file=log_img)
            else:
                await self.bot.logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass  # beta can't log
        if len(warns) >= 5:
            return await ctx.send(f"Warned {target}. This is warn #{len(warns)}. {log_msg}", embed=embed)
        await ctx.send(f"Warned {target}. This is warn #{len(warns)}. {log_msg}")

    @commands.command()
    @commands.has_any_role("Discord Moderator", "FlagBrew Team")
    async def delwarn(self, ctx, target: discord.User, *, warn):
        """Deletes a users warn. Can take the warn number, or the warn reason"""
        try:
            warnings = len(self.bot.warns_dict[str(target.id)])
            if warnings == 0:
                return await ctx.send(f"{target} doesn't have any warnings!")
        except KeyError:
            return await ctx.send(f"{target} hasn't been warned before!")
        if warn.isdigit() and warn not in self.bot.warns_dict[str(target.id)]:
            try:
                warn = self.bot.warns_dict[str(target.id)].pop(int(warn) - 1)
            except (KeyError):
                return await ctx.send(f"{target} doesn't have a warn with that number.")
        else:
            try:
                self.bot.warns_dict[str(target.id)].remove(warn)
            except ValueError:
                return await ctx.send(f"{target} doesn't have a warn matching `{warn}`.")
        if self.bot.is_mongodb:
            self.db['warns'].update_one(
                {
                    "user": str(target.id)
                },
                {
                    "$set": {
                        "user": str(target.id),
                        "warns": self.bot.warns_dict[str(target.id)]
                    }
                }, upsert=True)
        with open("saves/warns.json", "w") as file:
            json.dump(self.bot.warns_dict, file, indent=4)
        await ctx.send(f"Removed warn from {target}.")
        warns_count = len(self.bot.warns_dict[str(target.id)])
        embed = discord.Embed(title=f"Warn removed from {target}")
        embed.add_field(name="Warn Reason:", value=warn["reason"])
        embed.add_field(name="Warned By:", value=warn["warned_by"])
        if type(warn['date']) is float:  # Backwards compatibility
            warn_date = datetime.fromtimestamp(warn['date']).strftime("%D %H:%M:%S")
        else:
            warn_date = warn['date']
        date_obj = datetime.strptime(warn_date, "%m/%d/%y %H:%M:%S")
        embed.add_field(name="Warned On:", value=discord.utils.format_dt(date_obj))
        embed.set_footer(text=f"{target.name} now has {warns_count} warn(s).")
        try:
            await target.send(f"Warn `{warn['reason']}` was removed on {ctx.guild}. You now have {warns_count} warn(s).")
        except discord.Forbidden:
            embed.description += "\n**Could not DM user.**"
        try:
            await self.bot.logs_channel.send(f"{target} had a warn removed:", embed=embed)
        except discord.Forbidden:
            pass  # beta can't log

    @commands.command()
    @restricted_to_bot
    async def listwarns(self, ctx, target: discord.User = None):
        """Allows a user to list their own warns, or a staff member to list a user's warns"""
        if not target or target == ctx.author:
            target = ctx.author
        elif target and not any(role for role in [self.bot.discord_moderator_role, self.bot.flagbrew_team_role] if role in ctx.author.roles):
            raise commands.errors.CheckFailure()
            return
        try:
            warns = self.bot.warns_dict[str(target.id)]
        except KeyError:
            return await ctx.send(f"{target} has no warns.")
        embed = discord.Embed(title=f"Warns for {target}")
        count = 1
        for warn in warns:
            if type(warn['date']) is float:  # Backwards compatibility
                warn_date = datetime.fromtimestamp(warn['date']).strftime("%D %H:%M:%S")
            else:
                warn_date = warn['date']
            date_obj = datetime.strptime(warn_date, "%m/%d/%y %H:%M:%S")
            embed.add_field(name=f"#{count}: {discord.utils.format_dt(date_obj)}", value=f"**Reason**: {warn['reason']}\n**Issued By**: {warn['warned_by']}")
            count += 1
        if count - 1 == 0:
            return await ctx.send(f"{target} has no warns.")
        embed.set_footer(text=f"Total warns: {count - 1}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role("Discord Moderator", "FlagBrew Team")
    async def clearwarns(self, ctx, target: discord.User):
        """Clears all of a users warns"""
        try:
            warns = self.bot.warns_dict[str(target.id)]
            if len(warns) == 0:
                return await ctx.send(f"{target} doesn't have any warnings!")
            self.bot.warns_dict[str(target.id)] = []
        except KeyError:
            return await ctx.send(f"{target} already has no warns.")
        await ctx.send(f"Cleared warns for {target}.")
        if self.bot.is_mongodb:
            self.db['warns'].update_one(
                {
                    "user": str(target.id)
                },
                {
                    "$set": {
                        "user": str(target.id),
                        "warns": self.bot.warns_dict[str(target.id)]
                    }
                }, upsert=True)
        with open("saves/warns.json", "w") as file:
            json.dump(self.bot.warns_dict, file, indent=4)
        embed = discord.Embed(title=f"Warns for {target} cleared")
        embed.description = f"{target} | {target.id} had their warns cleared by {ctx.author}. Warns can be found below."
        count = 1
        for warn in warns:
            if type(warn['date']) is float:  # Backwards compatibility
                warn_date = datetime.fromtimestamp(warn['date']).strftime("%D %H:%M:%S")
            else:
                warn_date = warn['date']
            date_obj = datetime.strptime(warn_date, "%m/%d/%y %H:%M:%S")
            embed.add_field(name=f"#{count}: {discord.utils.format_dt(date_obj)}", value=f"**Reason**: {warn['reason']}\n**Issued By**: {warn['warned_by']}")
            count += 1
        try:
            await target.send(f"All of your warns were cleared on {ctx.guild}.")
        except discord.Forbidden:
            embed.description += "\n**Could not DM user.**"
        try:
            await self.bot.logs_channel.send(embed=embed)
        except discord.Forbidden:
            pass  # beta can't log


async def setup(bot):
    await bot.add_cog(Warning(bot))
