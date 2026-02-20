from __future__ import annotations

import asyncio
import random

from typing import TYPE_CHECKING, cast

import re
import os
import discord
from discord.ext import commands, tasks
from utils import NUM_REGEX

if TYPE_CHECKING:
    from main import AutoPostClient


async def setup(bot: AutoPostClient) -> None:
    await bot.add_cog(Bumper(bot))


class Bumper(commands.Cog):
    def __init__(self, bot: AutoPostClient):
        self.bot: AutoPostClient = bot

    async def cog_load(self) -> None:
        self.autobumper.start()

    async def cog_unload(self) -> None:
        self.autobumper.cancel()

    @commands.Cog.listener()
    async def on_bump_unready(self, message: discord.Message) -> None:
        embeds = message.embeds

        if embeds:
            regex = re.compile(NUM_REGEX)
            matches = list(filter(regex.search, str(embeds[0].description)))

            if matches:
                await asyncio.sleep(int(matches[0]) * 60)
                self.autobumper.restart()

    @tasks.loop(hours=2)
    async def autobumper(self):
        bump_channel = os.getenv("BUMP_CHANNEL")

        if not (bump_channel and bump_channel.isdigit()):
            return

        channel = self.bot.get_channel(int(bump_channel))
        random_delay = random.randint(6, 9)

        if channel and channel.guild and isinstance(channel, discord.TextChannel):
            check_perm = channel.permissions_for(cast(discord.Member, channel.guild.me))

            if not check_perm.send_messages:
                return

            bump = next(
                (
                    cmd
                    for cmd in await channel.application_commands()
                    if cmd.name == "bump"
                ),
                None,
            )

            if bump:
                try:
                    await asyncio.sleep(random_delay)
                    await bump()
                    self.bot.dispatch("client_bump", channel.guild)

                except Exception:
                    pass

    @autobumper.before_loop
    async def before_autobumper(self):
        await self.bot.wait_until_ready()
