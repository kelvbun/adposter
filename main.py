import os

import discord
import aiohttp

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class AutoPostClient(commands.Bot):
    channel_cache: list[int] = []

    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=str(os.getenv("PREFIX")),
            user_bot=True,
            case_insensitive=True,
            max_ratelimit_timeout=1,
            chunk_guilds_at_startup=True,
        )

    async def on_ready(self):
        assert isinstance(self.user, discord.ClientUser)
        
        print(f"logged on to: {self.user.name} | {self.user.id}")
        await self.change_presence(status=discord.Status.invisible)

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")

        with open("./storage/promo.txt", "r+") as f:
            f.seek(0)
            self.channel_cache = [int(id) for id in f.readlines()]

        f.close()
        print(self.channel_cache)


if __name__ == "__main__":
    bot = AutoPostClient()
    bot.run(str(os.getenv("TOKEN")), reconnect=True)
