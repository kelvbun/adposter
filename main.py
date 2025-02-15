import os

import aiohttp
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class adposter(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = aiohttp.ClientSession()
        self.webhook = os.getenv('WEBHOOK')

    async def on_ready(self):
        print(f'[200]: {self.user.name} | {self.user.id}')

    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')

if __name__ == '__main__':
    bot = adposter(command_prefix='-v-',
                   user_bot=True,
                   help_command=None,
                   case_insensitive=True,
                   max_ratelimit_timeout=1)

    bot.run(os.getenv('TOKEN'))
