from discord import app_commands
from discord.ext import commands


class NotOwner(app_commands.CheckFailure):
    pass


class NotWhiteListed(Exception):
    pass


class UnexpectedOutput(Exception):
    pass


class IncorrectGuild(commands.CheckFailure):
    pass
