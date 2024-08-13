import discord
import yt_dlp
from dotenv import load_dotenv
import asyncio

load_dotenv()

voice_clients = {}
yt_dl_options = {'format': 'bestaudio/best'}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)
ffmpeg_options = {'options': '-vn'}

async def play_music(ctx):
    if not ctx.author.voice:
        await ctx.send("You must be in a voice channel to use this command.")
        return

    channel = ctx.author.voice.channel

    try:
        voice_client = voice_clients.get(ctx.guild.id)
        if voice_client is None:
            voice_client = await channel.connect()
            voice_clients[ctx.guild.id] = voice_client
    except Exception as e:
        print(e)
        return

    try:
        url = ctx.message.content.split()[1]

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        song_url = data['url']
        player = discord.FFmpegOpusAudio(song_url, **ffmpeg_options)

        voice_client.play(player)
    except Exception as e:
        print(e)
