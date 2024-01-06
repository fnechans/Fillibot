import discord
from .disc import bot
from .utils import get_log, omluva
import asyncio

log = get_log()

import torch
from TTS.api import TTS


class Volume:
    value = 0.3


# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"


class MyTTS:
    ready = False
    tts = {}

    @staticmethod
    def setup():
        MyTTS.tts['en'] = TTS(
            model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False
        )
        MyTTS.tts['en2'] = TTS(
            model_name="tts_models/en/ljspeech/neural_hmm", progress_bar=False
        )
        MyTTS.tts['uk'] = TTS(
            model_name="tts_models/uk/mai/glow-tts", progress_bar=False
        )
        MyTTS.tts['de'] = TTS(
            model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False
        )
        MyTTS.tts['sk'] = TTS(
            model_name="tts_models/sk/cv/vits", progress_bar=False
        )
        MyTTS.tts['cs'] = TTS(
            model_name="tts_models/cs/cv/vits", progress_bar=False
        )
        MyTTS.ready = True


@bot.command(name='tts', help='Prehraje text, format $tts JAZYK TEXT')
@discord.ext.commands.guild_only()
async def _tts(ctx, lang, *, text):
    async with ctx.typing():
        if not MyTTS.ready:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: MyTTS.setup())
            # MyTTS.setup()
        if lang not in MyTTS.tts.keys():
            await ctx.send(f'Jazyk {lang} neni podporovan, podporuju pouze:')
            await ctx.send(f'Davej pozor ze je potreba zadat nejdriv jazyk,\n'
                           'takze format napr. "$tts sk moje zprava"')
            await ctx.send(f'{MyTTS.tts.keys()}')
            return
        try:
            voice_channel = ctx.message.author.voice.channel
            if (
                voice_channel is not None
                and ctx.voice_client is not None
                and ctx.voice_client.channel != voice_channel
            ):
                await ctx.send('Bot ted hraje v jinem voice kanalu!')
                return
            if voice_channel is None:
                await ctx.send('Musis byt pripojeny do voice kanalu!')
                return

            voice_client = ctx.voice_client

            if voice_client is None:
                # connect to voice channel
                voice_client = await voice_channel.connect()

            log.info(f'Language {lang}, text:')
            log.info(text)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: MyTTS.tts[lang].tts_to_file(text.replace("’", "'"), file_path="music/tts.wav"))
            log.info('Success!')
            filename = 'music/tts.wav'
            log.info(f'Filename {filename}')
            voice_client.play(
                discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(executable="ffmpeg", source=filename),
                    volume=Volume.value,
                )
            )
        except:
            await ctx.send('Problem s tts')


@bot.command(
    name='tts_volume', aliases=['tts_hlasitost'], help='Nastav hlasitost tts 0-100%'
)
async def volume(ctx, volume: int):
    voice_client = ctx.message.guild.voice_client
    if 0 <= volume <= 100:
        await ctx.send(f'Nastavuju volume na {volume}%')
        Volume.value = volume / 100
    else:
        await ctx.send('Hlasitost musi byt mezi 0-100')
        return

    if voice_client.is_playing():
        ctx.voice_client.source.volume = volume / 100
