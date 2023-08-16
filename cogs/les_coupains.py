import asyncio
from discord import app_commands
from discord.ext import commands

from mcstatus import JavaServer
from utils import exceptions

from utils.docker import MinecraftContainerManager

from config.config import (
    MINECRAFT_SERVER_IP,
    MINECRAFT_SERVER_PORT,
    MINECRAFT_CONTAINER_NAME_PREFIX,
    PERSONAL_GUILD_ID,
    PERSONAL_GUILD_ID_CHECK_ROLE,
)

class LesCoupains(commands.Cog):
    """A cog for me and my friends' discord server"""

    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        # self.bot.loop.create_task(self.update_stats())
        pass

    def cog_check(self, ctx) -> bool:
        if ctx.guild and ctx.guild.id == PERSONAL_GUILD_ID:
            return True
        raise exceptions.IncorrectGuild

    @commands.hybrid_command(
        "mc-status", description="Voir le status du serveur minecraft"
    )
    @commands.has_role(PERSONAL_GUILD_ID_CHECK_ROLE)
    @app_commands.guilds(PERSONAL_GUILD_ID)
    async def _mc_stats(self, ctx):
        server = await JavaServer.async_lookup(
            MINECRAFT_SERVER_IP + ":" + str(MINECRAFT_SERVER_PORT)
        )
        status = None
        names = None
        try:
            async with asyncio.timeout(2):
                status = await server.async_query()
            names = status.players.names
        except:
            status = await server.async_status()
            names = [p.name for p in status.players.sample]

        message = (
            f"Il y a **{status.players.online}** sur **{status.players.max}** joueurs en ligne.\n"
            ""
        )

        if status.players.online > 0:
            quantitatif = "Le joueur"
            if status.players.online > 1:
                quantitatif = "Les joueurs"
            message += quantitatif + " actuellement en ligne "
            quantitatif = "est: "
            if status.players.online > 1:
                quantitatif = "sont: "
            message += quantitatif + ", ".join(["**" + p + "**" for p in names])

        await ctx.send(message, ephemeral=True)

    @commands.hybrid_command(
        "mc-say", description="Écrire une annonce dans le serveur minecraft"
    )
    @commands.has_role(PERSONAL_GUILD_ID_CHECK_ROLE)
    @app_commands.guilds(PERSONAL_GUILD_ID)
    async def _mc_say(self, ctx, message):
        manager = MinecraftContainerManager(MINECRAFT_CONTAINER_NAME_PREFIX)
        await manager.tell(message)
        await ctx.send(
            f"Le message `{message}` a été envoyé avec succès.", ephemeral=True
        )

    @commands.hybrid_command(
        "mc-exec", description="Exécuter une commande dans le serveur"
    )
    @commands.has_role(PERSONAL_GUILD_ID_CHECK_ROLE)
    @app_commands.guilds(PERSONAL_GUILD_ID)
    async def _mc_exec(self, ctx, message):
        manager = MinecraftContainerManager(MINECRAFT_CONTAINER_NAME_PREFIX)
        output = await manager.exec_rcon(message)
        await ctx.send(f"```\n{output}```", ephemeral=True)


async def setup(bot):
    await bot.add_cog(LesCoupains(bot))
