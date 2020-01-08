import os
import random

import asyncio
import discord
from discord.ext import commands

from bot.db import Database
from bot.db import save_dbs
from bot.resources import _get_cogs
from bot.resources import Chances
from bot.resources import command_prefix
from bot.resources import OWNERS
from bot.token import TOKEN
from bot.utils import is_member_blacklisted
from bot.utils import is_member_registered


class ProxymonBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, case_insensitive=True)
        self._proxymon_ready = False
        self.command = "cls" if os.name == "nt" else "clear"

        for cog in _get_cogs():
            self.load_extension(cog)

            print("Loaded", cog)

    async def clear_screen(self, message: str = "", delay: float = None):
        print_break = "\n" * (1 if message == "" else 2)

        if delay is not None:
            await asyncio.sleep(delay)

        os.system(self.command)
        print(self.__class__.__name__, print_break, message, sep="")

    async def dm(self, member: discord.Member, message):
        try:
            await member.send(message)
        except discord.Forbidden:
            return False
        else:
            return True

    async def close(self):
        await save_dbs()
        await super().close()

    async def on_message(self, message):
        if await is_member_blacklisted(message.author):
            return

        if await is_member_registered(message.author):
            chance = random.randint(1, 100)

            if chance <= Chances.FIND.value:
                # display proxymon
                pass

        await self.process_commands(message)

    async def on_connect(self):
        await Database.get()
        await self.clear_screen(message="Established connection")

    async def on_ready(self):
        if self._proxymon_ready is False:
            self._proxymon_ready = True
            self.owners = {k: self.get_user(v) for k, v in OWNERS.items()}
            activity = discord.Game(f"p.about")

            await self.change_presence(activity=activity)
        await self.clear_screen(message="Connected")
        await self.clear_screen(delay=1)


proxymon = ProxymonBot(command_prefix=command_prefix)


if __name__ == "__main__":
    try:
        proxymon.run(TOKEN)
    except KeyboardInterrupt:
        print("Exited")
