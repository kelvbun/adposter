import discord
from discord.ext import commands


async def setup(bot) -> None:
    await bot.add_cog(Log(bot))


class Log(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener("on_member_ban")
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        if self.bot.user:
            return

        webhook = discord.Webhook.from_url(self.bot.webhook, session=self.bot.session)
        await webhook.send(f"{user} was banned from {guild}")

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        if self.bot.user:
            return

        webhook = discord.Webhook.from_url(self.bot.webhook, session=self.bot.session)
        await webhook.send(f"{member} was kicked from {member.guild}")
