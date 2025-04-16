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
        self.ad: str = ''
        self.ignored: dict[str, int] = {}
        self.invite_regex = r"(?:https?://)?discord(?:app)?\.(?:com/invite|gg)/[a-zA-Z0-9]+/?"
        self.channel_regex = r"(?:\b|[^a-zA-Z0-9])(?:sell|your?s?|you|clb?s?|collab?s?|ur-(?:promo|collab|shop|server)s?|urpromo?s?)(?:\b|[^a-zA-Z0-9])"
        self.path: dict = {
            "promo": "data/promo.txt",
            "shop": "data/shop.txt",
            "test-promo": "test-data/test-promo.txt",
            "test-shop": "test-data/test-shop.txt",
        }
        self.channel_cache: list[str] = []
        self.strip_channel_cache: list = []

    async def cog_unload(self) -> None:
        self.task_autopost.cancel()

    async def f_channels(self, guild: discord.Guild) -> list[str]:
        bucket: list[str] = []
        for channel in guild.channels:
            if re.search(self.channel_regex, channel.name, re.IGNORECASE) and isinstance(channel, discord.TextChannel):
                try:
                    messages = [message.content async for message in channel.history(limit=10, oldest_first=False)]
                    pattern = re.compile(self.invite_regex, re.IGNORECASE)
                    matches = list(filter(pattern.search, messages))

                    if len(matches) > 2:
                        bucket.append(str(channel.id))
                except discord.Forbidden:
                    continue #forbidden

        return bucket

    @tasks.loop(minutes=120)
    async def task_autopost(self) -> None:
        for channel_id in self.strip_channel_cache:
            random_delay = random.randint(6, 9)
            channel = self.bot.get_channel(int(channel_id))

            if channel and isinstance(channel, discord.TextChannel | discord.Thread):
                await asyncio.sleep(random_delay)
                await channel.send(self.ad)

    @task_autopost.before_loop
    async def before_auto_clock(self) -> None:
        await self.bot.wait_until_ready()

    @commands.command(name="scan")
    async def scan_channel(self, ctx: commands.Context, file: str) -> None:
        
        f_guilds = 0
        for folder in self.bot.settings.guild_folders:
            if folder.name == 'p':
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
                            if any(
                                aid.startswith(id) for aid in self.channel_cache
                            ):
                                continue
                            else:
                                f.write(f"{id}.{guild.id}\n")
                                self.channel_cache.append(f"{id}.{guild.id}\n")

            await ctx.send(f'scanned `{len(self.channel_cache)}/{f_guilds}` channels out of guilds')

        except KeyError:
            return print("[404]: no such path")

    @commands.command(name="send")
    async def send_channels(
        self, ctx: commands.Context, file: str
    ) -> None:
        try:
            file_path = self.path[file]

            with open(file_path, "r+") as f:
                f.seek(0)
                self.channel_cache = f.readlines()
                self.strip_channel_cache = [
                    id.split(".")[0] for id in self.channel_cache
                ]
                for id in self.strip_channel_cache:
                    random_delay = random.randint(5, 12)
                    await asyncio.sleep(random_delay)

                    try:
                        channel = self.bot.get_channel(int(id))
                        if isinstance(channel, discord.TextChannel) and channel.guild.id not in self.ignored.items():
                            history = [message.content async for message in channel.history(limit=1, oldest_first=False)]

                            if history and history[0] != self.ad:
                                try:
                                    await channel.send(self.ad)
                                except discord.RateLimited:
                                    continue

                    except None or discord.errors.Forbidden:
                        new_lines = [
                            line
                            for line in self.channel_cache
                            if line.strip() != id.strip()
                        ]
                        f.writelines(new_lines)
                        print("[404]: no such channel")

        except KeyError:
            print("[404]: no such path")

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

        except KeyError:
            return print("[404]: no such path")

        for page in paginator.pages:
            await ctx.send(page)

    @commands.command(name="set_clock")
    async def set_clock(self, ctx: commands.Context, min: int) -> None:
        os.environ["CLOCK"] = str(min)
        self.task_autopost.change_interval(minutes=min)
        await ctx.send(f"set auto post to every {min} mins")

    @commands.command(name="toggle_clock")
    async def toggle_clock(self, ctx: commands.Context) -> discord.Message | None:
        if self.task_autopost.is_running():
            self.task_autopost.cancel()
            return await ctx.send("turned off recurring posting")

        self.task_autopost.start()
        return await ctx.send("turned on recurring posting")

    @commands.command(name="set_ad")
    async def set_ad(self, ctx: commands.Context, *, ad: str) -> None:
        self.ad = ad
        pattern = re.compile(self.invite_regex, re.IGNORECASE)
        matches = pattern.findall(ad)

        for code in matches:
            try:
                invite = await self.bot.fetch_invite(code)
                self.ignored[code] = invite.guild.id

            except discord.NotFound:
                self.ignored.pop(code)
                continue

            except discord.HTTPException:
                continue

        await ctx.message.add_reaction('\U00002705')

            
