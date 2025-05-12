from __future__ import annotations

import asyncio
import logging
import random
from typing import cast
import os
import discord
from discord.ext import commands, tasks

logger = logging.getLogger(__name__)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Bumper(bot))


class Bumper(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def cog_load(self) -> None:
        self.autobumper.start()

    async def cog_unload(self) -> None:
        self.autobumper.cancel()

    @tasks.loop(hours=2)
    async def autobumper(self) -> None:
        channel = self.bot.get_channel(int(str(os.getenv("BUMP_CHANNEL"))))
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
                    logger.info(
                        f"[200]: bumped {channel.guild.name} | {channel.guild.id}"
                    )

                except Exception as e:
                    logger.error(f"[error]: {channel.guild.name}:\n{e}")

    @autobumper.before_loop
    async def before_autobumper(self):
        await self.bot.wait_until_ready()
