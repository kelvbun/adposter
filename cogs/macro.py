import asyncio
import random
import re

from typing import cast
import os

import discord
from discord.ext import commands, tasks


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Macro(bot))


class Macro(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.ad: str = ""
        self.ignored: dict[str, int] = {}
        self.invite_regex = (
            r"(?:https?://)?discord(?:app)?\.(?:com/invite|gg)/[a-zA-Z0-9]+/?"
        )
        self.channel_regex = r"(?:\b|[^a-zA-Z0-9])(?:sell|your?s?|you|clb?s?|collab?s?|ur-(?:promo|collab|shop|server)s?|urpromo?s?)(?:\b|[^a-zA-Z0-9])"
        self.channel_cache: list[str] = []
        self.path: dict = {
            "promo": "data/promo.txt",
            "test-promo": "data/test-promo.txt",
        }
        self.strip_channel_cache: list[str] = []

    async def cog_load(self) -> None:
        file_path = self.path["promo"]

        with open(file_path, "r+") as f:
            f.seek(0)
            self.channel_cache = f.readlines()
            self.strip_channel_cache = [id.split(".")[0] for id in self.channel_cache]

        f.close()
        print(self.strip_channel_cache)

    async def cog_unload(self) -> None:
        self.task_autopost.cancel()

    async def f_channels(self, guild: discord.Guild) -> list[str]:
        bucket: list[str] = []
        for channel in guild.channels:
            if re.search(
                self.channel_regex, channel.name, re.IGNORECASE
            ) and isinstance(channel, discord.TextChannel):
                try:
                    messages = [
                        message.content
                        async for message in channel.history(
                            limit=10, oldest_first=False
                        )
                    ]
                    pattern = re.compile(self.invite_regex, re.IGNORECASE)
                    matches = list(filter(pattern.search, messages))

                    if len(matches) > 2:
                        bucket.append(str(channel.id))
                except discord.Forbidden:
                    continue  # forbidden

        return bucket

    @tasks.loop(minutes=int(str(os.getenv("CLOCK"))))
    async def task_autopost(self) -> None:
        assert self.bot.user is not None

        self.strip_channel_cache = [id.split(".")[0] for id in self.channel_cache]
        for channel_id in self.strip_channel_cache:
            random_delay = random.randint(3, 5)
            channel = self.bot.get_channel(int(channel_id))

            if isinstance(channel, discord.TextChannel) and channel.guild.id not in list(self.ignored.values()):

                if not channel.guild.chunked:
                    await channel.guild.fetch_members(
                        channels=[channel], 
                        cache=True,
                        force_scraping=True,
                        delay=1.5
                    )

                await asyncio.sleep(15)

                history = [
                    message
                    async for message in channel.history(limit=2, oldest_first=False)
                ]

                if not history:
                    pass

                    if last_user:
                        if len(history) == 2 and history[0] != last_user.bot and history[1] != self.bot.user.id:
                            try:
                                await asyncio.sleep(random_delay)
                                await channel.send(self.ad)
                                self.bot.dispatch('client_send', self.ad)

                            except (discord.RateLimited, discord.HTTPException):
                                continue

                    elif len(history) == 1 and history[0] != self.bot.user.id:
                        try:
                            await asyncio.sleep(random_delay)
                            await channel.send(self.ad)

                    except (discord.RateLimited, discord.HTTPException):
                        continue

            else:
                continue

    @task_autopost.before_loop
    async def before_auto_clock(self) -> None:
        await self.bot.wait_until_ready()

    @commands.command(name="scan")
    async def scan_channel(self, ctx: commands.Context, file: str) -> None:
        f_guilds = 0

        if self.bot.settings:
            for folder in self.bot.settings.guild_folders:
                if folder.name == "p":
                    f_guilds = len(folder)

        try:
            file_path = self.path[file]
            filter_out = []

            with open(file_path, "r+") as f:
                f.seek(0)
                self.channel_cache = f.readlines()

                for guild in self.bot.guilds:
                    filter_out = await self.f_channels(guild)
                    if filter_out:
                        for id in filter_out:
                            if any(aid.startswith(id) for aid in self.channel_cache):
                                continue
                            else:
                                f.write(f"{id}.{guild.id}\n")
                                self.channel_cache.append(f"{id}.{guild.id}\n")

            f.close()
            await ctx.send(
                f"scanned `{len(self.channel_cache)}/{f_guilds}` channels out of guilds"
            )

        except KeyError:
            return print("[404]: no such path")

    @commands.command(name="send")
    async def send_channels(self, ctx: commands.Context, file: str) -> None:
        assert self.bot.user is not None

        try:
            file_path = self.path[file]

            with open(file_path, "r+") as f:
                f.seek(0)
                self.channel_cache = f.readlines()
                self.strip_channel_cache = [
                    id.split(".")[0] for id in self.channel_cache
                ]
                for id in self.strip_channel_cache:
                    random_delay = random.randint(3, 5)
                    await asyncio.sleep(random_delay)

                    try:
                        channel = self.bot.get_channel(int(id))
                        if isinstance(channel, discord.TextChannel) and channel.guild.id not in list(self.ignored.values()):

                            if not channel.guild.chunked:
                                await channel.guild.fetch_members(
                                    channels=[channel], 
                                    cache=True,
                                    force_scraping=True,
                                    delay=1.5
                                )

                            await asyncio.sleep(15)

                            history = [
                                message async for message in channel.history(
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
                                self.bot.dispatch('client_send', message)

                            except (discord.RateLimited, discord.HTTPException):
                                continue

                    except None or discord.errors.Forbidden:
                        new_lines = [
                            line for line in self.channel_cache
                            if line.strip() != id.strip()
                        ]

                        f.writelines(new_lines)
                        print("[404]: no such channel")

            f.close()

        except KeyError:
            print("[404]: no such path")

        await ctx.message.add_reaction("\U00002705")

    @commands.command(name="show")
    async def show_channels(self, ctx: commands.Context, file: str) -> None:
        try:
            file_path = self.path[file]
            paginator = commands.Paginator(prefix="", suffix="")

            with open(file_path, "r+") as f:
                f.seek(0)
                self.channel_cache = f.readlines()
                self.strip_channel_cache = [
                    id.split(".")[0] for id in self.channel_cache
                ]

                for id in self.strip_channel_cache:
                    channel = self.bot.get_channel(int(id))
                    if channel and isinstance(channel, discord.TextChannel):
                        if (
                            channel.permissions_for(
                                cast(discord.Member, ctx.author)
                            ).view_channel
                            and channel.permissions_for(
                                cast(discord.Member, ctx.author)
                            ).send_messages
                        ):
                            paginator.add_line(
                                f"[{channel.guild.name}]: {channel.mention if channel else 'invalid'}"
                            )
            f.close()

        except KeyError:
            return print("[404]: no such path")

        for page in paginator.pages:
            await ctx.send(page)

        await ctx.message.add_reaction("\U00002705")

    @commands.command(name="set_clock")
    async def set_clock(self, ctx: commands.Context, min: int) -> None:
        os.environ["CLOCK"] = str(min)
        self.task_autopost.change_interval(minutes=min)
        await ctx.send(f"set auto post to every {min} mins")

    @commands.command(name="toggle_clock")
    async def toggle_clock(self, ctx: commands.Context) -> discord.Message | None:
        if self.task_autopost.is_running():
            self.task_autopost.cancel()
            await ctx.send("turned off recurring posting")

        else:
            self.task_autopost.start()
            await ctx.send("turned on recurring posting")

    @commands.command(name="set_ad")
    async def set_ad(self, ctx: commands.Context, *, ad: str) -> None:
        self.ad = ad
        pattern = re.compile(self.invite_regex, re.IGNORECASE)
        matches = pattern.findall(ad)

        for code in matches:
            try:
                invite = await self.bot.fetch_invite(code)
                self.ignored[code] = invite.guild.id if invite.guild else 0

            except discord.NotFound:
                self.ignored.pop(code)
                continue

            except discord.HTTPException:
                continue

        await ctx.message.add_reaction("\U00002705")
