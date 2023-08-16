import asyncio

import os

import logging
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration

import aiohttp

import sentry_sdk

import discord
from discord.ext import commands

from config.config import DEFAULT_PREFIXES, TOKEN, SENTRY_DSN


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)-15s] %(message)s")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

err = "❌"
oop = "⚠"
ok = "✔"

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_HIDE"] = "True"


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or(*DEFAULT_PREFIXES),
            strip_after_prefix=True,
            intents=intents,
        )
        self.session = None
        self.initial_extensions = ["jishaku"]
        self.colour = self.color = discord.Colour(value=0xA37FFF)

    async def close(self):
        await self.session.close()

        logging.info("Closing the bot...")
        
        await super().close()

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_ready_once(self):
        await self.wait_until_ready()
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="you")
        )

    async def load_cogs(self):
        """
        Loads all the extensions in the ./cogs directory.
        """
        extensions = [
            f"cogs.{f[:-3]}"
            for f in os.listdir("./cogs")
            if f.endswith(".py")  # 'Cogs' folder
        ] + self.initial_extensions  # Initial extensions like jishaku or others that may be elsewhere
        for ext in extensions:
            try:
                await self.load_extension(ext)
                logging.info(f"{ok} Loaded extension {ext}")

            except Exception as e:
                if isinstance(e, commands.ExtensionNotFound):
                    logging.error(
                        f"{oop} Extension {ext} was not found {oop}", exc_info=False
                    )

                elif isinstance(e, commands.NoEntryPointError):
                    logging.error(
                        f"{err} Extension {ext} has no setup function {err}",
                        exc_info=False,
                    )

                else:
                    logging.error(
                        f"{err}{err} Failed to load extension {ext} {err}{err}",
                        exc_info=e,
                    )

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.load_cogs()
        self.loop.create_task(self.on_ready_once())


if __name__ == "__main__":

    async def main():
        sentry_logging = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                AsyncioIntegration(),
                sentry_logging,
            ],
        )
        bot = MyBot(intents=intents)
        async with bot:
            await bot.start(TOKEN)

    asyncio.run(main())
