from discord.ext import commands

from bot.exceptions import MemberNotRegistered
from bot.utils import create_embed
from bot.utils import get_tb_message


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_messages = {
            commands.MissingRequiredArgument: "Invalid arguments",
            MemberNotRegistered: ""
        }
        self.ignored_commands = [
            "me"
        ]
        self.ignored_errors = [
            commands.CommandNotFound,
            commands.CheckFailure,
            commands.BadArgument
        ]

    def is_ignored(self, ctx, error):
        result = [type(error) in self.ignored_errors]

        if ctx.command is not None:
            result.append(ctx.command.name in self.ignored_commands)
        return any(result)

    async def get_error_channel(self):
        return await self.bot.fetch_channel(505689773961117706)

    @commands.Cog.listener()
    async def on_error(self, event):
        print(">>> on_error:", type(event))

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        channel = ctx.channel

        if self.is_ignored(ctx, error):
            return
        if type(error) is commands.CommandInvokeError:
            error = error.original

        title = f"Error: {type(error).__name__}"
        desc = self.error_messages.get(type(error))

        if desc is None:
            channel = await self.get_error_channel()
            desc = (f"{ctx.author.mention}: `{ctx.message.content}`\n"
                    f"```py\n"
                    f"{get_tb_message(error)}\n"
                    f"```")

        await channel.send(embed=create_embed(title, desc))


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
