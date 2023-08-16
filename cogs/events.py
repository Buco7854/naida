import contextlib
import logging
import traceback
from sentry_sdk import capture_exception

import humanize

import discord
from discord import app_commands

from discord.ext import commands
from jishaku import math

from config.config import DEFAULT_PREFIXES
from utils import exceptions


async def setup(bot):
    await bot.add_cog(Events(bot))


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message_event(self, message):
        with contextlib.suppress(discord.HTTPException):
            if message.content in (f'<@{self.bot.user.id}>', f'<@!{self.bot.user.id}>'):
                display_prefixes = [f'`{p}`' for p in DEFAULT_PREFIXES]
                await message.reply(
                    f"Hi **{message.author.name}**, my prefix{'es are' if len(DEFAULT_PREFIXES) > 1 else ' is'} "
                    f"{', '.join(display_prefixes[0:-1]) if len(display_prefixes) > 1 else display_prefixes[0]}"
                    f"{' and ' + display_prefixes[-1] if len(display_prefixes) > 1 else ''}.",
                    mention_author=False
                )

    @commands.Cog.listener("on_command_error")
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(colour=ctx.bot.colour)
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CheckFailure):
            if isinstance(error, commands.BotMissingPermissions):
                missing = [(e.replace('_', ' ').replace('guild', 'server')).title() for e in error.missing_permissions]
                perms_formatted = "**, **".join(missing[:-2] + ["** and **".join(missing[-2:])])
                _message = f"I need the **{perms_formatted}** permission(s) to run this command."
                embed.title = "❌ Bot missing permissions"
                embed.description = _message
                await ctx.send(embed=embed, ephemeral=True)

            elif isinstance(error, commands.CommandOnCooldown):
                _message = f"This command is on cooldown, please retry in {humanize.time.precisedelta(math.ceil(error.retry_after))}. "
                embed.title = "🛑 Command on cooldown"
                embed.description = _message
                await ctx.send(embed=embed, ephemeral=True)

            elif isinstance(error, commands.MissingPermissions):
                missing = [(e.replace('_', ' ').replace('guild', 'server')).title() for e in error.missing_permissions]
                perms_formatted = "**, **".join(missing[:-2] + ["** and **".join(missing[-2:])])
                _message = f"You need the **{perms_formatted}** permission(s) to use this command."
                embed.title = "🛑 Missing permissions"
                embed.description = _message
                await ctx.send(embed=embed, ephemeral=True)

            elif isinstance(error, commands.MissingRole):
                missing = error.missing_role
                _message = f"You need the **{missing}** role to use this command."
                embed.title = "🛑 Missing role"
                embed.description = _message
                await ctx.send(embed=embed, ephemeral=True)

            elif isinstance(error, commands.NoPrivateMessage):
                return

            elif isinstance(error, exceptions.IncorrectGuild):
                return

            elif isinstance(error, (exceptions.NotOwner, commands.NotOwner)):
                _message = f"Sorry **{ctx.author}**, but this commmand is an owner-only command."
                embed.title = "🛑 Owner-only"
                embed.description = _message
                await ctx.send(embed=embed, ephemeral=True)
            else:
                embed.title = "🛑 Check Failure"
                embed.description = "You or the bot cannot run this command."
                await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, discord.Forbidden):
            embed.title = "🛑 Forbidden",
            embed.description = "Sorry I dont have enough permissions to do this."
            await ctx.send(embed=embed, ephemeral=True)
        elif isinstance(error, (commands.BadArgument, commands.BadLiteralArgument, commands.BadUnionArgument)):
            embed.title = "🛑 Bad Argument"
            embed.description = str(error)
            await ctx.send(embed=embed, ephemeral=True)
        else:
            embed.title = "❌ Error"
            embed.description = "Sorry, an error has occured, please retry later."
            embed.add_field(name="Traceback :", value=f"```py\n{type(error).__name__} : {error}```")
            traceback_string = "".join(traceback.format_exception(error, value=error, tb=error.__traceback__))
            logging.error(error, exc_info=(error, error, error.__traceback__))
            await ctx.send(embed=embed, ephemeral=True)
