import os

import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class Bao(commands.Bot):
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
        print(
            f"[200]: Bao has logged on to: {self.user.name} | {self.user.id}"
            if self.user
            else "[404]: Bao thinks the user token is invalid"
        )

        await self.change_presence(
            status=discord.Status.invisible,
        )

    async def load_promo(self) -> None:
        with open(self.file_path["promo"], "r+") as f:
            f.seek(0)
            self.channel_cache = [id.split(".")[0] for id in f.readlines()]

        f.close()
        print(self.channel_cache)

    async def setup_hook(self) -> None:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")

        await self.load_promo()


if __name__ == "__main__":
    bot = Bao()
    bot.run(str(os.getenv("TOKEN")), reconnect=True)
