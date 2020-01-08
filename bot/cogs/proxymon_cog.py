from math import floor
from typing import Union

import asyncio
from asyncio import TimeoutError
from discord.ext import commands

import bot.checks
from bot.db import Database
# from bot.db import Names
from bot.proxydex import Proxydex
from bot.proxymon import Starter
from bot.resources import START_COMMAND
from bot.types import Type
from bot.types import TypeDual
from bot.utils import create_embed
from bot.utils import is_member_registered
from bot.utils import send_with_embed


class ProxymonCog(commands.Cog, name="Proxymon"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["me"], usage="{0}profile\n"
                                          "{0}me")
    async def profile(self, ctx):
        """
        View your trainer profile if you have created one
        """
        author = ctx.author
        title = "You have not been created"
        desc = (f"You can create your own Proxymon trainer by doing "
                f"`{ctx.prefix}{START_COMMAND}`")
        fields = {}
        trainer_found = await is_member_registered(author)

        if trainer_found:
            title = str(author)
            desc = f"`{trainer_found.format_reg_date()}`"
            fields = {
                "Name": trainer_found.name,
                "Starter": trainer_found.starter,
                "Money": f"`{trainer_found.money:,}`",
                "Proxydex": str(trainer_found.proxydex),
                "New": "`Yes`" if trainer_found.is_new() else "`No`"
            }

        await send_with_embed(ctx, title, desc, fields=fields)

    @profile.command(name="create", usage=f"{{0}}{START_COMMAND}")
    async def profile_create(self, ctx):
        """
        The registration process - create your Proxymon trainer profile and
        start playing Proxymon
        """
        title = "Profile Creation"
        desc = "Are you a boy or a girl?"
        GENDERS = {
            "\U0001f1e7": "Male",
            "\U0001f1ec": "Female"
        }
        RANDOM = "\U0001f1f7"

        def check(reaction, member):
            return (member == ctx.author and
                    str(reaction.emoji) in GENDERS.keys())

        message = await send_with_embed(ctx, title, desc)

        for emoji in GENDERS.keys():
            await message.add_reaction(emoji)

        try:
            reaction = await self.bot.wait_for("reaction_add", check=check,
                                               timeout=30.0)
        except TimeoutError:
            return await message.clear_reactions()
        else:
            gender = GENDERS.get(reaction)

        def message_check(message):
            return message.author == ctx.author

        def reaction_check(reaction, member):
            return member == ctx.author and str(reaction.emoji) == RANDOM

        valid_name_given = False
        title = "Okay, and your name is?"
        desc = ("Max character length: 12\n"
                "If you'd like a random name, hit the R button down there.")

        while valid_name_given is False:
            message = await send_with_embed(ctx, title, desc)

            await message.add_reaction(RANDOM)

            completed, running = asyncio.wait([
                self.bot.wait_for("message", check=message_check,
                                  timeout=30.0),
                self.bot.wait_for("reaction_add", check=reaction_check,
                                  timeout=30.0)
            ], return_when=asyncio.FIRST_COMPLETED)

            try:
                name = completed.pop().result()
            except TimeoutError:
                return await message.clear_reactions()
            else:
                for task in running:
                    task.cancel()

                if type(name) is str and len(name) < 13:
                    valid_name_given = True
                else:
                    title = "That doesn't look quite right..."
                    desc = ("Please enter a valid name.\n"
                            "Max character length: 12\n"
                            "If you'd like a random name, hit the R button "
                            "down there.")

        print(gender)
        await ctx.send("lmao this shit aint finished")

    @commands.command(aliases=["dex"],
                      usage="{0}proxydex goatorch\n"
                            "{0}dex 4")
    @bot.checks.is_registered()
    async def proxydex(self, ctx, identifier: Union[int, str]):
        """
        View information on caught Proxymon
        """
        identifier = (identifier.title() if type(identifier) is str
                      else identifier)
        title = "???"
        desc = "???"
        fields = {
            "Types": "???"
        }
        trainer = await Database.get_trainer(ctx.author)
        proxymon = Proxydex.get_entry_by(identifier)
        met = trainer.proxydex.has_met(proxymon)
        caught = trainer.proxydex.has_caught(proxymon)

        if proxymon is None:
            title = "Proxymon not found"
            arg_type = type(identifier) is str and "name" or "entry number"
            desc = (f"There is no existing Proxymon with the {arg_type} "
                    f"`{identifier}`")
            fields = {}
        elif caught:
            title = f"Entry #{proxymon.id}: {proxymon.name}"
            desc = proxymon.description
            types = (type(proxymon.type) is Type and
                     proxymon.type.name.title() or
                     str(proxymon.type))
            fields["Types"] = types
        elif met:
            title = f"Entry #{proxymon.id}: {proxymon.name}"

        await send_with_embed(ctx, title, desc, fields=fields)

    @commands.command(aliases=["select"], usage="{0}starter xazela")
    @bot.checks.has_no_starter()
    async def starter(self, ctx, starter):
        """
        Choose the starter you want to use by name, this will officially
        register you as a Proxymon trainer
        """
        starter = starter.title()
        title = ctx.invoked_with.title()
        desc = (f"{starter} is not a starter Proxymon. To check what "
                f"starters there are, do `{ctx.prefix}starters`")
        starter_found = Starter.get_starter(starter)

        if starter_found:
            desc = (f"You have selected **{starter.title()}** to be your "
                    f"starter  Proxymon, make sure you take good care of it!")
            trainer = await Database.create_trainer(ctx.author)
            starter_found.calc_shiny()

            await trainer.edit(starter=starter_found.name)
            await trainer.add_to_team(starter_found)
            await Database.save_trainer(trainer)

        await send_with_embed(ctx, title, desc)

    @commands.command(usage="{0}starters")
    async def starters(self, ctx):
        """
        Displays the starter Proxymon that you can choose from
        """
        title = "Starters"
        desc = (f"These are the starters you can pick from. To select the "
                f"starter you want, do `{ctx.prefix}starter` followed by the "
                f"name. E.g. `{ctx.prefix}starter salaqua`")
        fields = {}

        for starter in Starter:
            proxymon = Proxydex.get_entry_by(starter.name.title())
            types = ""

            if type(proxymon.type) is Type:
                types = proxymon.type.name.title()
            elif type(proxymon.type) is TypeDual:
                types = str(proxymon.type)

            fields.setdefault(f"{proxymon.name} - {types}", proxymon.desc)

        await send_with_embed(ctx, title, desc, fields=fields)

    @commands.command(usage="{0}team\n"
                            "{0}team 1")
    @bot.checks.is_registered()
    async def team(self, ctx, position: int = None):
        """
        View your current team of Proxymon or the Proxymon in the given
        team position
        """
        trainer = await Database.get_trainer(ctx.author)
        fields = {}
        counter = 1
        FULL = "█"
        EMPTY = "▁"

        if position is None:
            team = trainer.team
        else:
            try:
                counter = position
                position -= 1
                team = trainer.team[position]
            except IndexError:
                pass

        if type(team) is list:
            for proxymon in team:
                if proxymon is None:
                    continue
                health = proxymon.stats.health
                shiny = proxymon.is_shiny() and ":sparkles:" or ""
                fainted = proxymon.fainted() and "`[FNT]`" or ""

                try:
                    diff = int(health.current / health.max) * 10
                except ZeroDivisionError:
                    diff = 0

                rem = diff == 0 and 10 or floor(diff % 10)

                key = f"[{counter}] {proxymon.name}"
                value = (f"Lv{proxymon.level} {shiny} {fainted}\n"
                         f"`{health.current} / {health.max} "
                         f"{FULL * diff}{EMPTY * rem}`")
                fields.setdefault(key, value)
                counter += 1

            await send_with_embed(ctx, fields=fields)
        else:
            counter = 0
            timed_out = False
            proxymon = team
            exp = proxymon.experience
            stats = proxymon.stats
            hp = stats.health
            shiny = proxymon.is_shiny() and ":sparkles:" or ""
            fainted = proxymon.fainted() and "`[FNT]`" or ""
            ability = proxymon.ability
            nature = proxymon.nature
            ptype = (type(proxymon.type) is Type and
                     proxymon.type.name.title() or
                     str(proxymon.type))
            digits = len(str(len(Proxydex.entries)))
            pid = f"No. {str(proxymon.id).zfill(digits)}"
            emojis = ["\U00002b05", "\U000027A1"]

            try:
                diff = int(exp.current / exp.max) * 20
            except ZeroDivisionError:
                diff = 0

            rem = diff == 0 and 20 or floor(diff % 20)

            pages = [
                create_embed(fields={
                    "Proxymon Info": pid,
                    "Profile": (f"**OT**/{trainer.name}\n"
                                f"**TYPE**/{ptype}"),
                    "Ability": (f"**{ability.name}**\n"
                                f"{ability.description}"),
                    "Trainer Memo": (f"**{nature.name}** nature,\n"
                                     f"met at Lv**{proxymon.level_met}**,\n"
                                     f"**{proxymon.met_at.name}**")
                }),
                create_embed(fields={
                    "Proxymon Skills": pid,
                    "Stats": (f"`HP {hp.current}/{hp.max}`\n"
                              f"`ATTACK {stats.attack.physical}`\n"
                              f"`DEFENSE {stats.defense.physical}`\n"
                              f"`SP. ATK {stats.attack.special}`\n"
                              f"`SP. DEF {stats.defense.special}`\n"
                              f"`SPEED {stats.speed}`"),
                    "Exp.": (f"`EXP. POINTS {exp.current}`\n"
                             f"`NEXT LV. {exp.needed}`\n"
                             f"`{FULL * diff}{EMPTY * rem}`")
                })
            ]

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in emojis

            message = await ctx.send(embed=pages[counter])

            for emoji in emojis:
                await message.add_reaction(emoji)

            while timed_out is False:
                try:
                    await self.bot.wait_for("reaction_add", timeout=30.0,
                                            check=check)
                except TimeoutError:
                    timed_out = True
                    await message.clear_reactions()
                else:
                    counter = (counter+1) % 2

                    await message.edit(embed=pages[counter])

    @commands.command(usage="{0}reset")
    @bot.checks.is_registered()
    async def reset(self, ctx):
        """
        Removes all of your data and allows you to start anew

        WARNING: Once this is done, you are unable to get your team, caught
        Proxymon or currency back no matter what! This is permanent!
        """
        THUMBS_UP = "\U0001f44d"
        trainer = await Database.get_trainer(ctx.author)
        title = "Reset"
        desc = "Are you sure you want to reset all of your progress?"
        fields = {
            # generate information on existing progress
        }
        message = await send_with_embed(ctx, title, desc, fields=fields)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == THUMBS_UP

        await message.add_reaction(THUMBS_UP)

        try:
            await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
        except TimeoutError:
            await message.clear_reactions()
        else:
            name = trainer.process_name(ctx.author)
            desc = (f"Your progress as `{name}` has been reset. Sorry to see "
                    f"you go...")
            embed = create_embed(title, desc)

            await message.edit(embed=embed)
            await Database.remove_trainer(ctx.author)


def setup(bot):
    bot.add_cog(ProxymonCog(bot))
