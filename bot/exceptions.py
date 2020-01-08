import discord
from discord.ext import commands


class BaseProxymonException(commands.errors.CommandError):
    def __init__(self, ctx, message):
        super().__init__(message)
        self.ctx = ctx


class MemberNotRegistered(BaseProxymonException):
    def __init__(self, ctx, message, member: discord.Member):
        super().__init__(ctx, message)
        self.member = member
