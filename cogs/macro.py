import asyncio
import random
import re

import discord
from discord.ext import commands
from openai import OpenAI


async def setup(bot) -> None:
    await bot.add_cog(macro(bot))


class macro(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.message_queue: dict = {}

        self.data = {
            "promo": "data/promo.txt",
            "shop": "data/shop.txt",
            "test-promo": "test-data/test-promo.txt",
            "test-shop": "test-data/test-shop.txt",
        }
        
        self.channel_name_pattern = r"(?:\b|[^a-zA-Z0-9])(?:sell|yours|your|you|clb|clbs|collab|collabs|ur-promo|ur-promos|ur-collabs|ur-collabs|ur-shop|ur-shops|ur-server|ur-servers|shop|shops|urpromo|urpromos)(?:\b|[^a-zA-Z0-9])"

        self.api_key = "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"
        self.openaiclient = OpenAI(api_key=self.api_key)


    @commands.command()
    async def send(self, ctx, file: str, *, message: str) -> None:

        """
        send a message to all channels in a file

        parameters
        file: str
            the file to read the channels from
        message: str
            the message to send to the channels
        """

        if self.data.get(file) is None:
            return await ctx.send(f"{file} was not found in the data dictionary")

        try:
            with open(self.data[file], "r") as f:
                lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            return await ctx.send(f"file {self.data[file]} was not found")
        
        queue_status = [f"- ``queue`` ﹕ sending. . .     ⸝⸝⸝     ``200 OK``"]
        status_message = await ctx.send("\n".join(queue_status))
        check_message = []

        for line in lines:
            try:
                # split and parse channel ids
                ids = [int(part.strip()) for part in line.split(" | ")]
                ids.pop(0)
            except ValueError:
                queue_status.append(f"- invalid line format: {line}")
                await status_message.edit(content="\n".join(queue_status))
                continue

            for channel_id in ids:
                channel = self.bot.get_channel(channel_id)
                random_delay = random.randint(5, 8)

                if channel:
                    try:
                        async for last_message in channel.history(limit=2, oldest_first=False):
                                
                            if not last_message.author.bot:
                                check_message.append(last_message.content) 
                        
                        if check_message and check_message[0] == message:
                            pass
                        else:
                            await channel.send(message) 
                        
                        check_message.clear()

                        #queue_status.append(f"- ``{channel.guild.name}`` ﹕ {channel.mention}     ⸝⸝⸝     ``200 OK``")
                    except discord.RateLimited:
                        queue_status.append(f"- ``{channel.guild.name}`` ﹕ {channel.mention}     ⸝⸝⸝     ``429 WARNING``")
                    except discord.Forbidden:
                        queue_status.append(f"- ``{channel.guild.name}`` ﹕ {channel.mention}     ⸝⸝⸝     ``403 WARNING``")
                    except discord.HTTPException as e:
                        queue_status.append(f"- ``{channel.guild.name}`` ﹕ {channel.mention}     ⸝⸝⸝     ``401 WARNING``")
                else:
                    queue_status.append(f"- invalid channel id: {channel_id}")

                await status_message.edit(content="\n".join(queue_status))
                await asyncio.sleep(random_delay)

        queue_status.append(f"-# finished executing at {ctx.message.created_at}")
        await status_message.edit(content="\n".join(queue_status))


    @commands.command(name="check")
    async def check(self, ctx, file: str) -> None:

        """
        check the channels in a file

        parameters
        file: str
            the file to read the channels from
        """

        if self.data.get(file) is None:
            return await ctx.send(f"{file} was not found")

        valid_channels = []
        invalid_channels = []
        channel_count = 0

        try:
            with open(self.data[file], "r") as f:
                # Sanitize and normalize raw data
                raw_data = [entry.strip() for entry in f.read().split("\n") if entry.strip()]

            structured_lines = []
            for line in raw_data:
                # Split and validate pairs
                if " | " in line:
                    parts = line.split(" | ")
                    if len(parts) == 2 and all(part.isdigit() for part in parts):
                        structured_lines.append(line)
                    else:
                        invalid_channels.append(line)
                else:
                    invalid_channels.append(line)

            with open(self.data[file], "w") as f:
                for line in structured_lines:
                    try:
                        guild_id, channel_id = map(int, line.split(" | "))
                        channel = self.bot.get_channel(channel_id)
                        channel_count += 1
                        if channel:
                            valid_channels.append(line)
                            #await asyncio.sleep(2)
                            #await ctx.send(f"- ``{channel.guild.name}`` ﹕ {channel.mention}     ⸝⸝⸝     ``200 OK``")
                        else:
                            invalid_channels.append(line)
                            await ctx.send(f"- ``{guild_id}`` ﹕ {channel_id}     ⸝⸝⸝     ``404 WARNING``")
                    except (ValueError, AttributeError):
                        invalid_channels.append(line)
                        await ctx.send(f"malformed line: {line}")

                f.writelines(f"{line}\n" for line in valid_channels)

            if invalid_channels:
                await ctx.send(f"- removed {len(invalid_channels)} invalid entries")

            await ctx.send(f"- ``{channel_count} channels`` ﹕ all checked ⸝⸝⸝     ``200 OK``")
            await ctx.send(f"-# finished executing at {ctx.message.created_at}")

        except Exception as e:
            await ctx.send(f"an error occurred: {e}")


    @commands.command(name="fetch_all")
    async def fetch_all(self, ctx, file: str) -> None:

        """
        analyze all channels in the guilds the bot is in
        """
        channel_count = 0
        guild_channel_stored = []

        try:
            if self.data.get(file) is None:
                return await ctx.send(f"{file} was not found")

            file_path = self.data[file]

            with open(file_path, "a") as promo_file:
                try:
                    existing_channels = {
                        int(line.strip().split(" | ")[1]) for line in open(file_path).readlines()
                    }
                except FileNotFoundError:
                    existing_channels = set()

                for guild in self.bot.guilds:
                    for channel in guild.text_channels:
                        
                        if guild.id in guild_channel_stored:  # Skip remaining channels if one has been stored
                            break

                        if re.search(self.channel_name_pattern, channel.name, re.IGNORECASE):
                            channel_permissions = channel.permissions_for(guild.me)

                            if not channel_permissions.send_messages:
                                continue

                            if channel.id in existing_channels:
                                continue
                            
                            promo_file.write(f"{guild.id} | {channel.id}\n")
                            channel_count += 1
                            guild_channel_stored.append(guild.id)
                            
            await ctx.send(f"- ``{channel_count} channels`` ﹕ all stored     ⸝⸝⸝     ``200 OK``")

        except Exception as e:
            await ctx.send(f"an error occurred: {e}")

        await ctx.send(f"-# finished executing at {ctx.message.created_at}")


    #show all channels in a promo
    @commands.command(name="show")
    async def show(self, ctx, file: str) -> None:
        if self.data.get(file) is None:
            pass

        try:
            with open(self.data[file], "r") as f:
                lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            pass

        for line in lines:
            try:
                ids = [int(part.strip()) for part in line.split(" | ")]
                ids.pop(0)
            except ValueError:
                pass

            for channel_id in ids:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await ctx.send(f"- ``{channel.guild.name}`` ﹕ {channel.mention}     ⸝⸝⸝     ``200 OK``")
                else:
                    await ctx.send(f"- invalid channel id: {channel_id}")

        await ctx.send(f"-# finished executing at {ctx.message.created_at}")