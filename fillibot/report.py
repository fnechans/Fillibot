import datetime
import discord
from discord.ext import commands, tasks

from fillibot.hltv import upcoming
from .utils import get_log

log = get_log()

utc = datetime.timezone.utc

# If no tzinfo is given then UTC is assumed.
time = datetime.time(hour=13, minute=48, tzinfo=utc)

class DailyReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.my_task.start()

    def cog_unload(self):
        self.my_task.cancel()

    @tasks.loop(time=time)
    async def my_task(self):
        log.info('Giving daily report!')
        guild = self.bot.get_guild(827799668179206145)
        channel = guild.get_channel(1182063938091884544)

        await channel.send('--- PRAVIDELNY DENNI REPORT ---')

        embed = discord.Embed(
            title='HLTV report',
            description='',
            color=discord.Color.blue(),
        )
        file = None
        try:
            file = discord.File("icons/hltv.png")
            embed.set_thumbnail(url='attachment://hltv.png')
        except:
            log.error('Failed to load file')
        for team in ['sinners', 'faze', 'witchers']:
            embed.add_field(name=team.upper(), value=upcoming(team), inline=False)
        await channel.send(embed=embed, file=file)


async def setup(bot):
    await bot.add_cog(DailyReport(bot))
