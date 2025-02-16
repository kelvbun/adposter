import asyncio
import random
import re
from typing import List

import os 

import discord
from discord.ext import commands, tasks


async def setup(bot) -> None:
    await bot.add_cog(Macro(bot))

class Macro(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.clock_toggled: bool = False
        self.ad: str = ''
        self.task_autopost.start()
        self.regex = r'(?:\b|[^a-zA-Z0-9])(?:sell|yours?|you|clb?s?|collab?s?|ur-(?:promo|collab|shop|server)s?|urpromo?s?)(?:\b|[^a-zA-Z0-9])'
        self.path: dict = {
            'promo': 'data/promo.txt',
            'shop': 'data/shop.txt',
            'test-promo': 'test-data/test-promo.txt',
            'test-shop': 'test-data/test-shop.txt',
        }
        self.channel_cache: List[str] = []
        self.strip_channel_cache = [id.split('.')[0] for id in self.channel_cache]
    
    def cog_unload(self) -> None:
        self.task_autopost.cancel()

    def f_channels(self, guild) -> List[str]:
        bucket: List[str] = []
        for channel in guild.channels:
            if re.search(self.regex, channel.name, re.IGNORECASE):
                bucket.append(str(channel.id))

        return bucket
    
    @tasks.loop(minutes = os.getenv('CLOCK'))
    async def task_autopost(self) -> None:
        if self.toggle_clock:
            for channel in self.strip_channel_cache:
                random_delay = random.randint(6, 9)
                channel = self.bot.get_channel(channel)
                
                await asyncio.sleep(random_delay)
                await channel.send(self.ad)

    @task_autopost.before_loop
    async def before_auto_clock(self) -> None:
        await self.bot.wait_until_ready()

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

                for id in self.strip_channel_cache:
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

                for id in self.strip_channel_cache:
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

    @commands.command(name = 'set_clock')
    async def set_clock(self, ctx: commands.Context, min: int) -> None:
        os.environ['CLOCK'] = min
        await ctx.send(f'set clock to: {min} mins')

    @commands.command(name = 'toggle_clock')
    async def toggle_clock(self, ctx: commands.Context) -> None:
        if self.clock_toggled:
            self.clock_toggled = False
            await ctx.send('turned off recurring posting')
        else:
            self.clock_toggled = True
            await ctx.send('turned on recurring posting')

    @commands.command(name = 'set_ad')
    async def set_ad(self, ctx: commands.Context, *, ad: str) -> None:
        self.ad = ad
        await ctx.send(ad)
            


    


    

        


    


        




        
