from __future__ import annotations

import asyncio
import random
import re

from typing import TYPE_CHECKING, cast
import os

import discord
from discord.ext import commands, tasks

if TYPE_CHECKING:
    from main import Bao


INVITE_REGEX = r"(?:https?://)?discord(?:app)?\.(?:com/invite|gg)/[a-zA-Z0-9]+/?"
CHANNEL_REGEX = r"(?:\b|[^a-zA-Z0-9])(?:sell|your?s?|you|clb?s?|collab?s?|ur-(?:promo|collab|shop|server)s?|urpromo?s?)(?:\b|[^a-zA-Z0-9])"


async def setup(bot: Bao) -> None:
    await bot.add_cog(Macro(bot))


class Macro(commands.Cog):
    def __init__(self, bot: Bao):
        self.bot: Bao = bot
        self.ad: str = ""
        self.ignored: dict[str, int] = {}

    async def cog_unload(self) -> None:
        self.task_autopost.cancel()

    async def find_channel(self, guild: discord.Guild) -> list[str]:
        bucket: list[str] = []
        for channel in guild.channels:
            if re.search(CHANNEL_REGEX, channel.name, re.IGNORECASE) and isinstance(
                channel, discord.TextChannel
            ):
                try:
                    messages = [
                        message.content
                        async for message in channel.history(
                            limit=10, oldest_first=False
                        )
                    ]

                    regex = re.compile(INVITE_REGEX, re.IGNORECASE)
                    matches = list(filter(regex.search, messages))

                    if len(matches) > 2:
                        bucket.append(str(channel.id))

                except discord.Forbidden:
                    continue  # forbidden

        return bucket

    @tasks.loop(minutes=int(str(os.getenv("CLOCK"))))
    async def task_autopost(self) -> None:
        assert self.bot.user is not None

        for channel_id in self.bot.channel_cache:
            random_delay = random.randint(3, 5)
            channel = self.bot.get_channel(int(channel_id))

            if isinstance(
                channel, discord.TextChannel
            ) and channel.guild.id not in list(self.ignored.values()):
                if not channel.guild.chunked:
                    await channel.guild.fetch_members(
                        channels=[channel], cache=True, force_scraping=True, delay=1.5
                    )

                await asyncio.sleep(15)

                history = [
                    message
                    async for message in channel.history(limit=2, oldest_first=False)
                ]

                if not history:
                    pass

                elif len(history) == 1:
                    if history[0].author.id == self.bot.user.id:
                        continue

                    else:
                        pass

                else:
                    last = history[0]
                    second_last = history[1]

                    if last.author.bot:
                        if second_last.author.id == self.bot.user.id:
                            continue

                        else:
                            pass

                    elif last.author.id == self.bot.user.id:
                        continue

                    else:
                        pass

                    try:
                        message = await channel.send(self.ad)
                        await asyncio.sleep(random_delay)
                        self.bot.dispatch("client_send", message)

                    except (discord.RateLimited, discord.HTTPException):
                        continue

            else:
                continue

    @task_autopost.before_loop
    async def before_auto_clock(self) -> None:
        await self.bot.wait_until_ready()

    @commands.command(name="scan")
    async def scan_channel(self, ctx: commands.Context, file: str) -> None:
        guild_count = 0

        if self.bot.settings:
            for folder in self.bot.settings.guild_folders:
                if folder.name == "p":
                    guild_count = len(folder)

        try:
            file_path = self.bot.file_path[file]
            filter_out = []

            with open(file_path, "r+") as f:
                for guild in self.bot.guilds:
                    filter_out = await self.find_channel(guild)

                    if filter_out:
                        for id in filter_out:
                            if any(
                                aid.startswith(id) for aid in self.bot.channel_cache
                            ):
                                continue

                            else:
                                f.write(f"{id}.{guild.id}\n")
                                self.bot.channel_cache.append(f"{id}.{guild.id}\n")

            f.close()

            await ctx.send(
                f"[200]: Bao scanned `{len(self.bot.channel_cache)}/{guild_count}` channels to guilds"
            )

        except KeyError:
            return print("[404]: no such path")

    @commands.command(name="send")
    async def send_channels(self, ctx: commands.Context, file: str) -> None:
        assert self.bot.user is not None

        try:
            for id in self.bot.channel_cache:
                random_delay = random.randint(3, 5)
                await asyncio.sleep(random_delay)

                try:
                    channel = self.bot.get_channel(int(id))
                    if isinstance(
                        channel, discord.TextChannel
                    ) and channel.guild.id not in list(self.ignored.values()):
                        if not channel.guild.chunked:
                            await channel.guild.fetch_members(
                                channels=[channel],
                                cache=True,
                                force_scraping=True,
                                delay=1.5,
                            )

                        await asyncio.sleep(15)

                        history = [
                            message
                            async for message in channel.history(
                                limit=2, oldest_first=False
                            )
                        ]

                        if not history:
                            pass

                        elif len(history) == 1:
                            if history[0].author.id == self.bot.user.id:
                                continue

                            else:
                                pass

                        else:
                            last = history[0]
                            second_last = history[1]

                            if last.author.bot:
                                if second_last.author.id == self.bot.user.id:
                                    continue

                                else:
                                    pass

                            elif last.author.id == self.bot.user.id:
                                continue

                            else:
                                pass

                        try:
                            message = await channel.send(self.ad)
                            await asyncio.sleep(random_delay)
                            self.bot.dispatch("client_send", message)

                        except (discord.RateLimited, discord.HTTPException):
                            continue

                except None or discord.errors.Forbidden:
                    pass  # too lazy to update the txt file

        except KeyError:
            print("[404]: Bao found no such path")

        await ctx.message.add_reaction("\U00002705")

    @commands.command(name="show")
    async def show_channels(self, ctx: commands.Context, file: str) -> None:
        await self.bot.load_promo()
    
        try:
            paginator = commands.Paginator(prefix="", suffix="")

            for id in self.bot.channel_cache:
                channel = self.bot.get_channel(int(id))

                if channel and isinstance(channel, discord.TextChannel):
                    perms = channel.permissions_for(cast(discord.Member, ctx.author))

                    if perms.view_channel and perms.send_messages:
                        paginator.add_line(
                            f"[{channel.guild.name}]: "
                            f"{channel.mention if channel else 'Invalid/Not Found'}"
                        )

        except KeyError:
            return print("[404]: Bao couldn't such path")

        for page in paginator.pages:
            await ctx.send(page)

        await ctx.message.add_reaction("\U00002705")

    @commands.command(name="set_clock")
    async def set_clock(self, ctx: commands.Context, min: int) -> None:
        os.environ["CLOCK"] = str(min)
        self.task_autopost.change_interval(minutes=min)
        await ctx.send(f"Bao has set auto post interval to every {min} mins")

    @commands.command(name="toggle_clock")
    async def toggle_clock(self, ctx: commands.Context) -> discord.Message | None:
        if self.task_autopost.is_running():
            self.task_autopost.cancel()
            await ctx.send("Bao has turned off auto posting")

        else:
            self.task_autopost.start()
            await ctx.send("Bao has turned on auto posting")

    @commands.command(name="set_ad")
    async def set_ad(self, ctx: commands.Context[Bao], *, ad: str) -> None:
        self.ad = ad
        regex = re.compile(INVITE_REGEX, re.IGNORECASE)
        matches = regex.findall(ad)

        for code in matches:
            try:
                invite = await self.bot.fetch_invite(code)
                self.ignored[code] = invite.guild.id if invite.guild else 0

            except discord.NotFound:
                continue

            except discord.HTTPException:
                continue

        await ctx.message.add_reaction("\U00002705")
