import asyncio
import random
import re

import discord
from discord.ext import commands

from typing import List


async def setup(bot) -> None:
    await bot.add_cog(Macro(bot))

class Macro(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.message_queue: dict = {}
        self.regex = r'(?:\b|[^a-zA-Z0-9])(?:sell|yours?|you|clb?s?|collab?s?|ur-(?:promo|collab|shop|server)s?|urpromo?s?)(?:\b|[^a-zA-Z0-9])'

        self.data = {
            "promo": "data/promo.txt",
            "shop": "data/shop.txt",
            "test-promo": "test-data/test-promo.txt",
            "test-shop": "test-data/test-shop.txt",
        }

    def fetch_channels(self, guild) -> List:
        bucket = []
        for channel in guild.channels:
            if re.search(self.regex, channel.name, re.IGNORECASE):
                bucket.append(channel.id)

        return bucket



