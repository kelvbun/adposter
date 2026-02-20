import os

import discord
import aiohttp

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class AutoPostClient(commands.Bot):
    channel_cache: list[str] = []
    file_path: dict[str, str] = {
        "promo": "data/promo.txt",
        "test-promo": "data/test-promo.txt",
    }

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

    async def load_promo(self) -> None:
        with open(self.file_path["promo"], "r+") as f:
            f.seek(0)
            self.channel_cache = [id.split(".")[0] for id in f.readlines()]

        f.close()
        print(self.channel_cache)

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")

        await self.load_promo()


if __name__ == "__main__":
    bot = AutoPostClient()
    bot.run(str(os.getenv("TOKEN")), reconnect=True)
