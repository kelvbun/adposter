import discord
import os

import aiohttp
from discord.ext import commands


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Log(bot))


class Log(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.session = aiohttp.ClientSession()
        self.webhook: str = str(os.getenv("WEBHOOK"))

    @commands.Cog.listener("on_member_ban")
    async def on_member_ban(self, guild: discord.Guild, member: discord.Member):
        if self.bot.user != member:
            return

        embed = discord.Embed(
            description=f"\U000026a0 {member}, you were banned from {guild.name}",
            color=discord.Color.red(),
        )
        webhook = discord.Webhook.from_url(self.webhook, session=self.session)
        
        await webhook.send(content=member.mention, embed=embed)

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        if self.bot.user != member:
            return

        embed = discord.Embed(
            description=f"\U000026a0 {member}, you were removed from {member.guild.name}",
            color=discord.Color.red(),
        )
        webhook = discord.Webhook.from_url(self.webhook, session=self.session)

        await webhook.send(content=member.mention, embed=embed)

    @commands.Cog.listener("on_message")
    async def mention_logger(self, message: discord.Message) -> None:
        if self.bot.user and self.bot.user.mention not in message.content:
            return

        embed = discord.Embed(description=f"```{message.content}```")
        webhook = discord.Webhook.from_url(self.webhook, session=self.session)
        
        await webhook.send(
            content=f"a user has [pinged]({message.jump_url}) client:", embed=embed
        )

    @commands.Cog.listener()
    async def on_client_send(self, message: discord.Message) -> None:
        assert message.guild is not None # dispatch on ad posting only

        embed = discord.Embed(description=f"```{message.content}```")
        webhook = discord.Webhook.from_url(self.webhook, session=self.session)

        await webhook.send(
            content=f"client sent a [message]({message.jump_url}) in **{message.guild.name}**:", embed=embed
        )

    @commands.Cog.listener()
    async def on_client_bump(self, guild: discord.Guild) -> None:
        embed = discord.Embed(description=f"{guild.id} | {guild.name}")
        webhook = discord.Webhook.from_url(self.webhook, session=self.session)

        await webhook.send(
            content=f"client has bumped **{guild.name}**:", embed=embed
        )