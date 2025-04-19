import os

import aiohttp
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class adposter(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_ready(self):
        print(
            f"[200]: {self.user.name} | {self.user.id}"
            if self.user
            else "uhhhh some shit"
        )
        await self.change_presence(
            status=discord.Status.online,
        )  # activity=discord.CustomActivity("free ad post bot in about me"),

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        self.webhook = os.getenv("WEBHOOK")
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")


if __name__ == "__main__":
    bot = adposter(
        command_prefix=str(os.getenv("PREFIX")),
        user_bot=True,
        case_insensitive=True,
        chunk_guilds_at_startup=True,
        max_ratelimit_timeout=1,
    )

    bot.run(str(os.getenv("TOKEN")))
    