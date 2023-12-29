# bot.py
import os

import discord # 2.3.2!!
from dotenv import load_dotenv
from fillibot import disc 

import logging


discord.utils.setup_logging()
log = logging.getLogger('discord')
log.setLevel(logging.INFO)
file_handler = logging.FileHandler('debug.log', mode = 'a')
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
file_handler.setFormatter(formatter)
log.addHandler(file_handler)


if __name__ == "__main__" :
    load_dotenv()
    disc.run()