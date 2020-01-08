import collections
import importlib
import io
import json
import textwrap
from contextlib import redirect_stdout
from typing import Union

import discord
from discord.ext import commands

import bot.checks
from bot.db import Database
from bot.utils import is_member_blacklisted
from bot.utils import send_with_embed


class Developer(commands.Cog, command_attrs={"hidden": True}):
    def __init__(self, bot):
        self.bot = bot

    def parse_code(self, code):
        if code.startswith("```") and code.endswith("```"):
            code = ("\n").join(code.split("\n")[1:-1])

        indented = textwrap.indent(code, " "*4)
        function = (f"async def function():\n"
                    f"{indented}")

        return function

    @bot.checks.is_owner()
    async def cog_check(self, ctx):
        return True

    @commands.group(invoke_without_command=True)
    async def blacklist(self, ctx,
                        member: Union[discord.Member, discord.User]):
        if type(member) is int:
            member = self.bot.get_user(member)

        if await bot.db.Blacklist.add(member) is not False:
            await ctx.message.add_reaction("👍")
        else:
            await ctx.message.add_reaction("👎")

        try:
            await self.bot.dm(
                member,
                ("**YOU HAVE BEEN BLACKLISTED**\n\n"

                 "If you would like to know why or appeal for your removal "
                 "from the blacklist, please consult the owners of Proxymon "
                 "in the Proxymon server.\n\n"

                 "Thank you for reading.")
            )
        except discord.Forbidden:
            pass

    @blacklist.command(name="check")
    async def blacklist_check(self, ctx,
                              member: Union[discord.Member, discord.User]):
        if type(member) is int:
            member = self.bot.get_user(member)

        if await is_member_blacklisted(member):
            return await ctx.message.add_reaction("👍")
        return await ctx.message.add_reaction("👎")

    @blacklist.command(name="remove")
    async def blacklist_delete(self, ctx,
                               member: Union[discord.Member, discord.User]):
        if type(member) is int:
            member = self.bot.get_user(member)

        if await is_member_blacklisted(member):
            await bot.db.Blacklist.remove(member)
        await ctx.message.add_reaction("👍")

    @commands.command()
    async def close(self, ctx):
        await ctx.message.add_reaction("👍")
        await self.bot.close()

    @commands.command()
    async def set(self, ctx, member: discord.Member, **attribs):
        trainer = await Database.get_trainer(member)
        await trainer.edit(**attribs)
        await Database.save_trainer(trainer)

    @commands.command(name="eval")
    @bot.checks.is_owner("DJ")
    async def _eval(self, ctx, *, code):
        code = self.parse_code(code)
        stdout = io.StringIO()
        env = {
            **globals(),
            "self": self,
            "ctx": ctx,
            "trainer": await Database.get_trainer(ctx.author)
        }

        async with ctx.channel.typing():
            try:
                exec(code, env)
            except Exception as e:
                result = f"{type(e).__name__}: {e}"
            else:
                function = env.get("function")

                try:
                    with redirect_stdout(stdout):
                        result = await function()
                except Exception as e:
                    result = f"{type(e).__name__}: {e}"
                else:
                    if result is None:
                        result = stdout.getvalue()

                    if isinstance(result, collections.Iterable):
                        result = json.dumps(result, indent=4)
                finally:
                    if result == "\"\"":
                        result = None
                    result = str(result)

        await ctx.send(result)

    @commands.command(name="import")
    @bot.checks.is_owner()
    async def _import(self, ctx, module_name):
        title = module_name.title()
        desc = "Successfully imported!"

        try:
            globals()[module_name] = importlib.import_module(module_name)
        except Exception as e:
            desc = (f"Importing failed\n\n"
                    f"{type(e).__name__} - {e}")

        await send_with_embed(ctx, title, desc)


def setup(bot):
    bot.add_cog(Developer(bot))
