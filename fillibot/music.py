import discord
import asyncio
import os
from urllib import parse
from urllib.request import urlopen  # , HTTPError, Request
from .youtube import YTDLSource
from .disc import bot
from .utils import get_log, omluva
import re

log = get_log()


class Volume:
    value = 0.03


queue = {}


@bot.command(
    name='play',
    aliases=['zahraj', 'p'],
    help='Zahraje song (prvni vysledek search na youtube)',
)
async def play(ctx, *, search):
    query_string = parse.urlencode({'search_query': search})
    html_content = urlopen('http://www.youtube.com/results?' + query_string)
    search_content = html_content.read().decode()
    search_results = re.findall(r'\/watch\?v=[a-zA-Z0-9-_]+', search_content)
    # print(search_results)
    url = 'https://www.youtube.com' + search_results[0]
    await ctx.invoke(bot.get_command('play_url'), url=url)


@bot.command(name='play_url', help='Zahraje song podle url')
@discord.ext.commands.guild_only()
async def play_url(ctx, url):
    async with ctx.typing():

        server = ctx.message.guild
        voice_channel = ctx.message.author.voice.channel
        if (
            voice_channel is not None
            and ctx.voice_client is not None
            and ctx.voice_client.channel != voice_channel
        ):
            await ctx.send('Bot ted hraje v jinem voice kanalu!')
            return

        if server.id not in queue.keys() or ctx.voice_client is None or not ctx.voice_client.is_playing():
            if voice_channel is None:
                await ctx.send('Musis byt pripojeny do voice kanalu!')
                return
            queue[server.id] = [url]
            await play_audio(server.id, ctx)
        else:
            queue[server.id].append(url)
            await ctx.send(f'Pridano do fronty, delka fronty je {len(queue[server.id])} ...')


async def play_audio(server_id, ctx):
    old_activity = bot.activity
    old_status = bot.status
    while len(queue[server_id]) != 0:
        voice_client = ctx.voice_client

        if voice_client is None:
            # connect to voice channel
            voice_channel = ctx.message.author.voice.channel
            voice_client = await voice_channel.connect()

        if len(queue[server_id]) == 0:
            await voice_client.disconnect()
            return
        url = queue[server_id][0]
        try:
            metadata = await YTDLSource.from_url(url, loop=bot.loop)
            log.info(f'Filename {metadata.filename}')
        except:
            log.error(f'Failed to download {url}')
            queue[server_id].pop(0)
            continue

        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=metadata.creator))

        voice_client.play(
            discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(executable="ffmpeg", source=metadata.filename),
                volume=Volume.value,
            ),
        )
        embed = discord.Embed(
            title=metadata.title,
            color=discord.Color.red(),
        )
        embed.add_field(name='Tvurce', value=metadata.creator)
        embed.set_thumbnail(url=metadata.thumbnail)
        await ctx.send(embed=embed)
        while voice_client.is_playing() or voice_client.is_paused():
            await asyncio.sleep(5)

        if len(queue[server_id])!= 0: # might be if stopped!
            queue[server_id].pop(0)
        os.remove(metadata.filename)
        await bot.change_presence(status=old_status, activity=old_activity)


@bot.command(name='pause', aliases=['pauza'], help='Pauzne song')
@discord.ext.commands.guild_only()
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("Bot zrovna nic nehraje.")


@bot.command(name='resume', aliases=['pokracuj'], help='Pokracuje v prehravani songu')
@discord.ext.commands.guild_only()
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send('Bot zrovna nic nehraje')


@bot.command(name='skip', help='Skipss the song')
@discord.ext.commands.guild_only()
async def skip(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send('Bot zrovna nic nehraje')

@bot.command(name='stop', help='Stops the song')
@discord.ext.commands.guild_only()
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        queue[ctx.message.guild.id] = []
    else:
        await ctx.send('Bot zrovna nic nehraje')


@bot.command(name='volume', aliases=['hlasitost'], help='Nastav hlasitost 0-100%')
async def volume(ctx, volume: int):
    voice_client = ctx.message.guild.voice_client
    if 0 <= volume <= 100:
        await ctx.send(f'Nastavuju volume na {volume}%')
        Volume.value = volume / 500
    else:
        await ctx.send('Hlasitost musi byt mezi 0-100')
        return

    if voice_client.is_playing():
        ctx.voice_client.source.volume = volume / 500
