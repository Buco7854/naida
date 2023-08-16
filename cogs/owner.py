import os
import typing

import discord
from discord.ext import commands


async def setup(bot):
    await bot.add_cog(Owner(bot))


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx) -> bool:
        if await self.bot.is_owner(ctx.author):
            return True
        raise commands.NotOwner()

    @commands.group(name='dev', aliases=['d'], invoke_without_command=True, hidden=True, message_command=True)
    async def dev(self, ctx, subcommand: str = None):
        if subcommand:
            return await ctx.send(f'Unknown subcommand `{subcommand}`', delete_after=5)

    @dev.command(name='restart', aliases=['reboot', 'r'], message_command=True)
    async def dev_restart(self, ctx, *, service: str = 'ayane'):
        await ctx.send("Restarting the bot...")
        await ctx.bot.close()

    Status = typing.Literal['playing', 'streaming', 'listening', 'watching', 'competing']

    @dev.command(name='status', aliases=['ss'], message_command=True)
    async def dev_status(self, ctx, status: Status, *, text: str):
        activity_types = {
            'playing': discord.ActivityType.playing,
            'streaming': discord.ActivityType.streaming,
            'listening': discord.ActivityType.listening,
            'watching': discord.ActivityType.watching,
            'competing': discord.ActivityType.competing,
        }
        extras = {}
        if status == 'streaming':
            extras['url'] = 'https://youtu.be/dQw4w9WgXcQ'
        await self.bot.change_presence(activity=discord.Activity(type=activity_types[status], name=text, **extras))
        await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
