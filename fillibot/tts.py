import discord
from .disc import bot
from .utils import get_log, omluva

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

    def setup():
        MyTTS.tts['en'] = TTS(
            model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False
        )  # .t .to(device)
        MyTTS.tts['sk'] = TTS(
            model_name="tts_models/sk/cv/vits", progress_bar=False
        )  # .t .to(device)
        MyTTS.ready = True


@bot.command(name='tts', help='Prehraje text, format $tts JAZYK TEXT')
@discord.ext.commands.guild_only()
async def _tts(ctx, lang, *, text):
    if not MyTTS.ready:
        MyTTS.setup()
    if lang not in MyTTS.tts.keys():
        await ctx.send(f'Jazyk {lang} neni podporovan, podporuju pouze:')
        await ctx.send(f'Davej pozor ze je potreba zadat nejdriv jazyk,\n'
                       'takze format napr. "$tts sk moje zprava"')
        await ctx.send(f'{MyTTS.tts.keys()}')
        return
    try:
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            log.info(f'Language {lang}, text:')
            log.info(text)
            MyTTS.tts[lang].tts_to_file(text, file_path="music/tts.wav")
            log.info('Success!')
            filename = 'music/tts.wav'
            log.info(f'Filename {filename}')
            voice_channel.play(
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
