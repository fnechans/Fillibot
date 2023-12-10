# bot.py
import os

import discord # 2.3.2!!
from dotenv import load_dotenv
from fillibot import hltv_upcoming 

from typing import List
import logging

discord.utils.setup_logging()
log = logging.getLogger('discord')
log.setLevel(logging.INFO)
file_handler = logging.FileHandler('debug.log', mode = 'a')
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

class Fillibot(discord.Client):
    async def on_ready(self):
        log.info(f'{client.user} has connected to Discord!')

        log.info(f'{client.user} is connected to the following guild:')
        for guild in client.guilds:
            log.info(f'{guild.name}(id: {guild.id})')

        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')


    async def on_message(self, message):
        if message.author == self.user or not message.content.startswith('$'):
            return

        log.info(f'User {message.author} wrote:')
        content : List[str] = [x for x in message.content[1:].split(' ') if x != '']
        log.info(content)

        command = content[0].lower()

        if command in ['cus', 'cau', 'ahoj', 'hi', 'hello', 'hallo']:
            await message.channel.send(f'Čau {message.author}!')
        if command == 'hltv':
            if len(content) != 2:
                await message.channel.send('Ocekavam zpravu ve tvaru "$ hltv TEAM_NAME"!')
                return
            team_name = content[1]
            match_sin = hltv_upcoming(team_name)
            await message.channel.send(match_sin)

client = Fillibot(intents=intents)
client.run(TOKEN, log_handler=None)