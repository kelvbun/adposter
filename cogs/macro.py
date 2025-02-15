import asyncio
import random
import re
from typing import List

import discord
from discord.ext import commands


async def setup(bot) -> None:
    await bot.add_cog(Macro(bot))

class Macro(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.regex = r'(?:\b|[^a-zA-Z0-9])(?:sell|yours?|you|clb?s?|collab?s?|ur-(?:promo|collab|shop|server)s?|urpromo?s?)(?:\b|[^a-zA-Z0-9])'
        self.path: dict = {
            'promo': 'data/promo.txt',
            'shop': 'data/shop.txt',
            'test-promo': 'test-data/test-promo.txt',
            'test-shop': 'test-data/test-shop.txt',
        }
        self.channel_cache: List[str] = []

    def f_channels(self, guild):
        bucket: List[str] = []
        for channel in guild.channels:
            if re.search(self.regex, channel.name, re.IGNORECASE):
                bucket.append(str(channel.id))

        return bucket

    @commands.command(name = 'scan')
    async def scan_channel(self, ctx: commands.Context, file: str) -> None:
        try:
            file_path = self.path[file]
            filter_out = []

            with open(file_path, "r+") as f:
                f.seek(0)
                self.channel_cache = f.readlines()

                for guild in self.bot.guilds:
                    filter_out = self.f_channels(guild)
                    if filter_out:
                        for id in filter_out:
                            if any(aid.startswith(id) for aid in self.channel_cache): # do i make a cache system (?)
                                pass
                            else:
                                f.write(f"{id}.{guild.id}\n")
                                
        except KeyError:
            return print('[404]: no such path') 
        
        await ctx.send(self.channel_cache)


    @commands.command(name = 'send')
    async def send_channels(self, ctx: commands.Context, file: str, *, arg: str) -> None:
        try:
            file_path = self.path[file]

            with open(file_path, "r+") as f:
                f.seek(0)
                self.channel_cache = f.readlines()
                strip_channel_cache = [id.split('.')[0] for id in self.channel_cache]

                for id in strip_channel_cache:
                    random_delay = random.randint(5, 12)
                    await asyncio.sleep(random_delay)
                    
                    try:
                        channel = self.bot.get_channel(int(id))
                        await channel.send(arg)

                    except None or discord.errors.Forbidden:
                        new_lines = [line for line in self.channel_cache if line.strip() != id.strip()]
                        f.writelines(new_lines)
                        print('[404]: no such channel')

        except KeyError:
            return print('[404]: no such path')
        
        await ctx.send(self.channel_cache)

    @commands.command(name = 'show')
    async def show_channels(self, ctx: commands.Context, file: str) -> None:
        try:
            file_path = self.path[file]

            with open(file_path, "r+") as f:
                f.seek(0)
                self.channel_cache = f.readlines()
                strip_channel_cache = [id.split('.')[0] for id in self.channel_cache]

                for id in strip_channel_cache:
                    try:
                        channel = self.bot.get_channel(int(id))
                        if channel:
                            await asyncio.sleep(3)
                            await ctx.send(channel.mention)

                    except None or discord.errors.Forbidden:
                        new_lines = [line for line in self.channel_cache if line.strip() != id.strip()]
                        f.writelines(new_lines)
                        print('[404]: no such channel')

        except KeyError:
            return print('[404]: no such path')
        
        await ctx.send(self.channel_cache)

    


    

        


    


        




        
