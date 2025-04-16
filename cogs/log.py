import discord
from discord.ext import commands


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Log(bot))


class Log(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener("on_member_ban")
    async def on_member_ban(self, guild: discord.Guild, member: discord.User | discord.Member):
        if self.bot.user != member:
            return

        embed = discord.Embed(description=f'\U000026a0 {member}, you were banned from {guild}', color=discord.Color.red())
        webhook = discord.Webhook.from_url(self.bot.webhook, session=self.bot.session)
        await webhook.send(content=member.mention, embed=embed)

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        if self.bot.user != member:
            return

        embed = discord.Embed(description=f'\U000026a0 {member}, you were kicked from {guild}', color=discord.Color.red())
        webhook = discord.Webhook.from_url(self.bot.webhook, session=self.bot.session)
        await webhook.send(content=member.mention, embed=embed)

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message) -> None:
        if message.author != self.bot.user:
            return
        
        embed = discord.Embed(description=f'```{message.content}```')
        webhook = discord.Webhook.from_url(self.bot.webhook, session=self.bot.session)
        await webhook.send(content=f'client sent a [message]({message.jump_url}):', embed=embed)

    @commands.Cog.listener("on_message_delete")
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author != self.bot.user:
            return
        
        embed = discord.Embed(description=f'```{message.content}```')
        webhook = discord.Webhook.from_url(self.bot.webhook, session=self.bot.session)
        await webhook.send(content='client deleted a message:', embed=embed)


        

