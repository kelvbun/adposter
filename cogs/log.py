from __future__ import annotations


from typing import TYPE_CHECKING
import discord
import os

import aiohttp
from discord.ext import commands

if TYPE_CHECKING:
    from main import Bao


async def setup(bot: Bao) -> None:
    await bot.add_cog(Logger(bot))


class Logger(commands.Cog):
    def __init__(self, bot: Bao):
        self.bot: Bao = bot
        self.session = aiohttp.ClientSession()
        self.webhook: str = str(os.getenv("WEBHOOK"))

    @commands.Cog.listener("on_member_ban")
    async def on_client_banned(self, guild: discord.Guild, member: discord.Member):
        if self.bot.user != member:
            return

        embed = discord.Embed(
            description=f"\U000026a0 {member}, you were banned from {guild.name}",
            color=discord.Color.red(),
        )
        webhook = discord.Webhook.from_url(self.webhook, session=self.session)

        await webhook.send(content=member.mention, embed=embed)

    @commands.Cog.listener("on_member_remove")
    async def on_client_kicked(self, member: discord.Member):
        if self.bot.user != member:
            return

        embed = discord.Embed(
            description=f"\U000026a0 {member}, you were removed from {member.guild.name}",
            color=discord.Color.red(),
        )
        webhook = discord.Webhook.from_url(self.webhook, session=self.session)

        await webhook.send(content=member.mention, embed=embed)

    @commands.Cog.listener("on_message")
    async def on_client_mentioned(self, message: discord.Message) -> None:
        if message.author.id == 302050872383242240:
            if message.embeds:
                if message.embeds[0].description and message.embeds[
                    0
                ].description.startswith("Please wait"):
                    self.bot.dispatch("on_bump_unready", message)

        if self.bot.user and self.bot.user.mention not in message.content:
            return

        embed = discord.Embed(description=f"```{message.content}```")
        webhook = discord.Webhook.from_url(self.webhook, session=self.session)

        await webhook.send(
            content=f"a user has [pinged]({message.jump_url}) client:", embed=embed
        )

    @commands.Cog.listener()
    async def on_client_send(self, message: discord.Message) -> None:
        assert message.guild is not None  # dispatch on ad posting only

        embed = discord.Embed(description=f"```{message.content}```")
        webhook = discord.Webhook.from_url(self.webhook, session=self.session)

        await webhook.send(
            content=f"client sent a [message]({message.jump_url}) in **{message.guild.name}**:",
            embed=embed,
        )

    @commands.Cog.listener()
    async def on_client_bump(self, guild: discord.Guild) -> None:
        embed = discord.Embed(description=f"{guild.id} | {guild.name}")
        webhook = discord.Webhook.from_url(self.webhook, session=self.session)

        await webhook.send(content=f"client has bumped **{guild.name}**:", embed=embed)
