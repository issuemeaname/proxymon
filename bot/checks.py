from discord.ext import commands

import bot.db
from bot.exceptions import MemberNotRegistered
from bot.locations import Location
from bot.resources import OWNERS
from bot.utils import create_embed
from bot.utils import is_member_blacklisted
from bot.utils import is_member_registered

MESSAGES = {
    "unregistered": (
        "It seems that you don't exist",
        ("You have not been registered as a trainer. To register yourself, "
         "check through the starters by doing `{0}starters`. When you have a "
         "starter you want to pick, do `{0}starter` followed by the name.\n\n"
         "E.g. `{0}starter salaqua`")
    ),
    "starter": (
        "Alright, I have good news and I have bad news...",
        ("The bad news is that you already have a starter, meaning you cannot "
         "pick a new one. The good news is that this means you're a trainer "
         "and can collect, fight and train Proxymon.")
    )
}


def is_owner(name: str = None):
    def predicate(ctx):
        """
        Verify if author is one of the owners
        """
        if name is None:
            return ctx.author.id in [v for v in OWNERS.values()]
        return ctx.author.id == OWNERS.get(name)
    return commands.check(predicate)


def is_registered():
    async def predicate(ctx):
        """
        Return if whether or not the author has been registered to the
        Proxymon bot.db.Database
        """
        member = ctx.author

        if await is_member_registered(member):
            return True
        raise MemberNotRegistered(ctx, str(member.id), member)

        title, desc = MESSAGES.get("unregistered")
        desc = desc.format(ctx.prefix)

        await ctx.send(embed=create_embed(title, desc))
        return False
    return commands.check(predicate)


def is_not_registered():
    async def predicate(ctx):
        """
        Return True if trainer is not registered in the database, otherwise
        return False
        """
        if await is_member_registered(ctx.author):
            return False


def has_no_starter():
    async def predicate(ctx):
        """
        Checksum for whether or not a trainer has a starter Proxymon
        """
        trainer = await bot.db.Database.get_trainer(ctx.author)
        message = None
        ret = True

        if trainer is not None and trainer.starter:
            message = "starter"
            ret = False

        message = MESSAGES.get(message)

        if message is not None:
            title, desc = message

            await ctx.send(embed=create_embed(title, desc))
        return ret
    return commands.check(predicate)


def is_trainer_at(location: Location):
    async def predicate(ctx):
        """
        Checksum for whether the author's current location is the supplied
        location
        """
        trainer = await bot.db.Database.get_trainer(ctx.author)
        return trainer.at_location(location)
    return commands.check(predicate)


def is_blacklisted():
    async def predicate(ctx):
        """
        Check if author is a blacklisted member
        """
        return await is_member_blacklisted(ctx.author)
    return commands.check(predicate)
