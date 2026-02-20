from __future__ import annotations

import asyncio
import random
import re

from typing import TYPE_CHECKING, cast
from pathlib import Path
import os

import discord
from discord.ext import commands, tasks
from utils import INVITE_REGEX

if TYPE_CHECKING:
    from main import AutoPostClient


async def setup(bot: AutoPostClient) -> None:
    await bot.add_cog(Macro(bot))


class Macro(commands.Cog):
    def __init__(self, bot: AutoPostClient):
        self.bot = bot
        self.ads: dict[str, str] = {}  # name -> content
        self.ignored: dict[str, int] = {}
        self.ads_path = Path("./storage/ads")

    async def cog_load(self) -> None:
        self.load_ads()
        self.autopost.start()

    async def cog_unload(self) -> None:
        self.autopost.cancel()

    def load_ads(self) -> None:
        self.ads.clear()
        self.ads_path.mkdir(parents=True, exist_ok=True)

        for file in self.ads_path.glob("*.txt"):
            content = file.read_text(encoding="utf-8").strip()
            if content:
                self.ads[file.stem] = content

    async def find_channel(self, guild: discord.Guild) -> list[str]:
        bucket: list[str] = []
        regex = re.compile(INVITE_REGEX, re.IGNORECASE)

        for channel in guild.channels:
            if not isinstance(channel, discord.TextChannel):
                continue
            try:
                messages = [
                    message async for message in channel.history(limit=10, oldest_first=False)
                ]
                matches = list(filter(lambda m: regex.search(m.content), messages))
                unique_authors = {m.author.id for m in matches}

                if len(matches) > 5 and len(unique_authors) > 2:
                    bucket.append(str(channel.id))
                    break

            except discord.Forbidden:
                pass

        return bucket

    @tasks.loop(minutes=int(str(os.getenv("CLOCK"))))
    async def autopost(self) -> None:
        assert isinstance(self.bot.user, discord.ClientUser)

        if not self.ads:
            return

        for channel_id in self.bot.channel_cache:
            random_delay = random.randint(3, 5)
            channel = self.bot.get_channel(channel_id)

            if isinstance(channel, discord.TextChannel) and channel.guild.id not in list(self.ignored.values()):
                history = [
                    message
                    async for message in channel.history(limit=2, oldest_first=False)
                ]

                if len(history) == 1:
                    if history[0].author.id == self.bot.user.id:
                        continue

                else:
                    last = history[0]
                    second_last = history[1]

                    if last.author.bot:
                        if second_last.author.id == self.bot.user.id:
                            continue

                    elif last.author.id == self.bot.user.id:
                        continue

                try:
                    ad = random.choice(list(self.ads.values()))
                    message = await channel.send(ad)
                    await asyncio.sleep(random_delay)
                    self.bot.dispatch("client_send", message)

                except (discord.RateLimited, discord.HTTPException):
                    continue

    @autopost.before_loop
    async def before_auto_clock(self) -> None:
        await self.bot.wait_until_ready()

    @commands.command(name="reload_ads")
    async def reload_ads(self, ctx: commands.Context) -> None:
        self.load_ads()
        await ctx.send(f"loaded `{len(self.ads)}` ads: {', '.join(f'`{n}`' for n in self.ads)}")

    @commands.command(name="list_ads")
    async def list_ads(self, ctx: commands.Context) -> discord.Message | None:
        if not self.ads:
            return await ctx.message.add_reaction("\U0000274c")

        paginator = commands.Paginator(prefix="", suffix="")
        for name, content in self.ads.items():
            paginator.add_line(f"`{name}`: {content[:80]}{'...' if len(content) > 80 else ''}")

        for page in paginator.pages:
            await ctx.send(page)

    @commands.cooldown(1, 7200, commands.BucketType.user)
    @commands.command(name="set_ad")
    async def set_ad(self, ctx: commands.Context[AutoPostClient], name: str, *, ad: str) -> None:
        file = self.ads_path / f"{name}.txt"
        file.write_text(ad, encoding="utf-8")
        self.ads[name] = ad

        regex = re.compile(INVITE_REGEX, re.IGNORECASE)
        for code in regex.findall(ad):
            try:
                invite = await self.bot.fetch_invite(code)
                self.ignored[code] = invite.guild.id if invite.guild else 0
            except (discord.NotFound, discord.HTTPException):
                continue

        await ctx.message.add_reaction("\U00002705")

    @commands.command(name="update_ad")
    async def update_ad(self, ctx: commands.Context, name: str, *, ad: str) -> discord.Message | None:
        file = self.ads_path / f"{name}.txt"

        if not file.exists():
            return await ctx.message.add_reaction("\U0000274c")

        file.write_text(ad, encoding="utf-8")
        self.ads[name] = ad
        await ctx.message.add_reaction("\U00002705")

    @commands.command(name="delete_ad")
    async def delete_ad(self, ctx: commands.Context, name: str) -> discord.Message | None:
        file = self.ads_path / f"{name}.txt"

        if not file.exists():
            return await ctx.message.add_reaction("\U0000274c")

        file.unlink()
        self.ads.pop(name, None)
        await ctx.message.add_reaction("\U00002705")

    @commands.command(name="scan")
    async def scan_channel(self, ctx: commands.Context) -> None:
        guild_count = 0

        if self.bot.settings:
            for folder in self.bot.settings.guild_folders:
                if folder.name == "p":
                    guild_count = len(folder)

        try:
            with open("./storage/promo.txt", "a") as f:
                for guild in self.bot.guilds:
                    for id in await self.find_channel(guild):
                        if any(str(aid).startswith(id) for aid in self.bot.channel_cache):
                            continue
                        f.write(f"{id}\n")
                        self.bot.channel_cache.append(int(id))

            await ctx.send(
                f"scanned `{len(self.bot.channel_cache)}` channels / `{guild_count}` guilds"
            )

        except OSError:
            print("no such path")

    @commands.command(name="show")
    async def show_channels(self, ctx: commands.Context) -> None:
        paginator = commands.Paginator(prefix="", suffix="")

        for id in self.bot.channel_cache:
            channel = self.bot.get_channel(int(id))

            if channel and isinstance(channel, discord.TextChannel):
                perms = channel.permissions_for(cast(discord.Member, ctx.author))

                if perms.view_channel and perms.send_messages:
                    paginator.add_line(
                        f"[{channel.guild.name}]: "
                        f"{channel.mention if channel else 'invalid'}"
                    )

        for page in paginator.pages:
            await ctx.send(page)

        await ctx.message.add_reaction("\U00002705")

    @commands.command(name="set_clock")
    async def set_clock(self, ctx: commands.Context, min: int) -> discord.Message | None:
        os.environ["CLOCK"] = str(min)
        self.autopost.change_interval(minutes=min)
        return await ctx.message.add_reaction("\U00002705")

    @commands.command(name="toggle_clock")
    async def toggle_clock(self, ctx: commands.Context) -> discord.Message | None:
        if self.autopost.is_running():
            self.autopost.cancel()
            return await ctx.message.add_reaction("\U00002705")

        self.autopost.start()
        await ctx.message.add_reaction("\U000023f0")
