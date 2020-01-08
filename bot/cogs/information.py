# import discord
from discord.ext import commands

from bot.resources import INVITE
from bot.resources import START_COMMAND
from bot.utils import create_embed
from bot.utils import send_with_embed


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @commands.command()
    async def about(self, ctx):
        """
        Gives an explanation on Proxymon as a whole
        """
        title = ctx.command.name.title()
        fields = {
            "What is Proxymon?": (
                "Proxymon is a project game based off of it's own version of "
                "Nintendo's Pokemon, which is more commonly referred to as "
                "Fakemon. Just like the original, you are allowed to choose "
                "and train your own starter Proxymon, which leads into "
                "developing a team of up to 6 and challenging other trainers "
                "in the same server"
            ),
            "How do I start?": (
                f"To begin your adventure, you must first create your profile "
                f"through `{ctx.prefix}{START_COMMAND}` You can then follow "
                f"the instructions given to you once you are done creating it."
            )
        }

        await send_with_embed(ctx, title, fields=fields)

    @commands.command()
    async def credit(self, ctx):
        """
        Displays the creators of Proxymon
        """
        fields = {k: str(v) for k, v in self.bot.owners.items()}

        await send_with_embed(ctx, fields=fields)

    @commands.group()
    async def prefix(self, ctx):
        """
        Shows the prefixes that can be used for Proxymon
        """
        prefixes = await self.bot.command_prefix(self.bot, ctx.message)
        title = ctx.command.name.title()
        desc = ""

        for prefix in prefixes:
            if prefix.find("@") != -1:
                desc += prefix
            else:
                desc += f"`{prefix}`"
            desc += "\n"

        await send_with_embed(ctx, title, desc)

    @commands.command(usage="{0}invite")
    async def invite(self, ctx):
        """
        Send the invite URL to invite Proxymon
        """
        embed = create_embed(
            title=ctx.command.name.title(),
            desc=f"[Here]({INVITE})"
        )

        await ctx.send(embed=embed)

    @commands.command(name="help", aliases=["h"],
                      usage="{0}help\n"
                            "{0}help starter")
    async def _help(self, ctx, command: str = ""):
        """
        Shows all of the commands in their respective groups or describes a
        command with given instructions and examples
        """
        title = None
        desc = None
        fields = {}
        command_found = self.bot.get_command(command)
        hidden_cogs = ["Developer"]

        if command_found and command_found.cog_name not in hidden_cogs:
            prefix = ctx.prefix
            title = command.title()
            desc = command_found.help
            aliases = [f"`{v}`" for v in command_found.aliases]
            usage = [f"`{v}`" for v in command_found.usage.split("\n")]
            fields = {
                "Aliases": (", ").join(aliases),
                "Usage": ("\n").join(usage).format(
                    prefix
                )
            }
        elif command == "":
            title = "Commands"
            desc = (f"To start playing Proxymon, do "
                    f"`{ctx.prefix}{START_COMMAND}`")

            for cog in sorted(self.bot.cogs):
                if cog in hidden_cogs:
                    continue

                name = cog
                cog = self.bot.get_cog(cog)
                cmds = []

                for cmd in cog.walk_commands():
                    if cmd.hidden is False:
                        cmds.append(cmd.name.title())

                if cmds:
                    fields.setdefault(name, (", ").join(sorted(cmds)))
        else:
            title = "Command not found"
            desc = (f"There is no `{command}` command that exists. If you "
                    f"would like to make a suggestion then feel free to join "
                    f"the Proxymon server and submit one - so long as it is "
                    f"rational it will at least be considered at the bare "
                    f"minimum.")

        await send_with_embed(ctx, title, desc, fields=fields)


def setup(bot):
    bot.add_cog(Information(bot))
