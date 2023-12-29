import discord  # 2.3.2!!
from discord.ext import commands, tasks

from .utils import get_log, omluva
from . import report
from .hltv import upcoming

log = get_log()

_intents = discord.Intents.default()
_intents.message_content = True
_intents.members = True

client = discord.Client(intents=_intents)
activity = discord.Activity(type=discord.ActivityType.listening, name="$help")
bot = commands.Bot(command_prefix='$', intents=_intents, activity=activity, status=discord.Status.idle)


def run():
    import os

    TOKEN = os.getenv('DISCORD_TOKEN')
    bot.run(TOKEN, log_handler=None)


@bot.event
async def on_ready():
    log.info("Bot is ready!")
    cogs = [report]
    for cog in cogs:
        await cog.setup(bot)
    log.info("Cogs synced!")


@bot.command(
    name='ahoj',
    aliases=['cus', 'cau', 'hi', 'hello', 'hallo', 'zdar', 'hey'],
    help='Pozdrav ...',
)
async def ahoj(ctx):
    await ctx.send(f'Čau {ctx.message.author}!')


@bot.command(help="Prints details of Server/Channel")
@discord.ext.commands.is_owner()
async def where_am_i(ctx):
    owner = str(ctx.guild.owner)
    guild_id = str(ctx.guild.id)
    memberCount = str(ctx.guild.member_count)
    desc = ctx.guild.description

    embed = discord.Embed(
        title=ctx.guild.name + " Server Information",
        description=desc,
        color=discord.Color.blue(),
    )
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="ID", value=guild_id, inline=True)
    embed.add_field(name="Member Count", value=memberCount, inline=True)
    await ctx.send(embed=embed)

    async for member in ctx.guild.fetch_members(limit=150):
        await ctx.send(
            'Name : {}\t Status : {}\n Joined at {}'.format(
                member.display_name, str(member.status), str(member.joined_at)
            )
        )

    guild_id = str(ctx.channel.id)

    embed = discord.Embed(
        title=ctx.channel.name + " Channel Information",
        color=discord.Color.orange(),
    )
    embed.add_field(name="ID", value=guild_id, inline=True)
    await ctx.send(embed=embed)


@bot.command(name='hltv', help='Vypise nadchazejici zapasy teamu')
async def hltv(ctx, *content):
    if len(content) != 1:
        await ctx.message.channel.send('Ocekavam zpravu ve tvaru "$hltv TEAM_NAME"!')
        return
    team_name = content[0]
    match_sin = upcoming(team_name)
    await ctx.message.channel.send(match_sin)
