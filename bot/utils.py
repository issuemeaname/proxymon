import textwrap
import traceback
from datetime import datetime
from random import randint
from typing import Union

import discord


def get_license():
    return f"issuemeaname | MIT Copyright © {datetime.now().year}"


def create_embed(title=None, desc=None, inline=False,
                 colour=discord.Colour(randint(1, 256**3-1)),
                 fields: dict = {}, author: discord.Member = None,
                 image: Union[discord.File, discord.Asset] = "",
                 thumbnail: Union[discord.File, discord.Asset] = ""):
    footer = get_license()
    embed = discord.Embed(title=title, description=desc, colour=colour)
    embed.set_footer(text=footer)

    for name, value in fields.items():
        embed.add_field(name=name, value=value, inline=inline)

    if type(image) is discord.File:
        image = f"attachment://{image.filename}"
    if type(thumbnail) is discord.File:
        thumbnail = f"attachment://{image.filename}"

    embed.set_image(url=image)
    embed.set_thumbnail(url=thumbnail)

    if author:
        embed.set_author(name=str(author), icon_url=author.avatar_url)

    return embed


def get_tb_message(error, newline="\n"):
    newline = newline or ""
    tracebacks = ("").join(traceback.format_tb(error.__traceback__))

    return textwrap.dedent(tracebacks) + newline + (f"{type(error).__name__}: "
                                                    f"{error}")


def get_timezone():
    return str(datetime.utcnow().astimezone().tzinfo).split()[0]


def proxymon_dump(obj):
    return obj and obj.dump()


async def is_member_registered(member: discord.Member):
    from bot.db import Database

    return await Database.get_trainer(member)


async def is_member_blacklisted(member: discord.Member):
    from bot.db import Blacklist

    return await Blacklist.check(member)


async def send_with_embed(ctx, *args, **kwargs):
    return await ctx.send(embed=create_embed(*args, **kwargs))
