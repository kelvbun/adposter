import asyncio

import discord
from discord.ext import commands
from PyCharacterAI import get_client
from PyCharacterAI.exceptions import SessionClosedError


async def setup(bot) -> None:
    await bot.add_cog(cai(bot))


class cai(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = "a91798ff29991f1e4136813cd8fdb09ea9338b61"
        self.character_id = "5wpTBOYDgP77sgtsDXQshV7cIDXJaoP0ZVVZdMdDa6A"
    

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):

        m = ""

        if message.author == self.bot.user:
            return

        if message.author.bot:
            return
        
        if message.channel.id != 1315834738841358377:
            return 

        if message.content.startswith("rinn"):
            async with message.channel.typing():
                client = await get_client(token=self.token)

            me = await client.account.fetch_me()

            chat, greeting_message = await client.chat.create_chat(self.character_id)

            try:
                answer = await client.chat.send_message(self.character_id, chat.chat_id, m)
                await asyncio.sleep(2)
                await message.channel.send(answer.get_primary_candidate().text)

            except SessionClosedError:
                print("session closed. Bye!")

        #finally:
            # Don't forget to explicitly close the session
            #await client.close_session()
            



    