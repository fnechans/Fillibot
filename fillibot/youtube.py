import yt_dlp as youtube_dl
import discord
import asyncio
import os
from .utils import get_log, omluva
log = get_log()

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
class YTMetadata:
    def __init__(self, filename, creator, title, thumbnail):
        self.filename = filename
        self.creator = creator
        self.title = title
        self.thumbnail = thumbnail

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))
        if data is None:
            log.error('Failed to download')
            raise RuntimeError
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = ytdl.prepare_filename(data)
        os.makedirs('music', exist_ok=True)
        if not os.path.exists(f'music/{filename}'): # TODO: check before download
            os.rename(filename, f'music/{filename}')
        else:
            os.remove(filename)
        return YTMetadata(f'music/{filename}', data['channel'], data['title'], data['thumbnail'])
