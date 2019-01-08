# import discord
from discord.ext import commands

from bot.resources import OWNERS
from bot.token import TOKEN


class Proxymon(commands.Bot):
    def __init__(self):
        self.owners = OWNERS

    async def on_connect(self, ctx):
        pass

    async def on_ready(self, ctx):
        pass


proxymon = Proxymon()

if __name__ == "__main__":
    proxymon.run(TOKEN)
