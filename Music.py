import discord
from discord.ext import commands  # importing commands from discord extension
import yt_dlp
import asyncio
from dotenv import load_dotenv
import re

load_dotenv()


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client

    # Initialize variables for music functionality
    queues = {}
    voice_clients = {}
    yt_dl_options = {'format': 'bestaudio/best'}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                      'options': '-vn -filter:a "volume=0.25"'}

    @commands.command(pass_context=True,
                      description='Bot will join the voice channel if user is already present.')
    async def join(self, ctx):
        # if user joins voice channel then bot will join voice channel
        if (ctx.author.voice):
            channel = ctx.message.author.voice.channel
            await channel.connect()
        # if user is NOT in voice channel
        else:
            await ctx.send("You are not in a voice channel, you must be in voice channel to run this command.")

    @commands.command(pass_context=True,
                      description='Bot will leave the voice channel.')
    async def leave(self, ctx):
        # if bot is in voice channel, then it'll leave and send a message.
        # diff from ctx.author.voice because it's based on the bot's action not the user's
        if (ctx.voice_client):
            await ctx.guild.voice_client.disconnect()
            await ctx.send("I left the voice channel.")
        # if bot is NOT in voice channel
        else:
            await ctx.send("I am not in a voice channel.")

    # cycles through songs using pop() as they get played and removed from the queue dictionary
    # not an event or command because doesn't exist in discord api
    async def play_next(self, ctx):
        if self.queues[ctx.guild.id] != []:
            link = self.queues[ctx.guild.id].pop(
                0)  # pop takes first song in queue, puts into link area and removes it from queue
            await self.play(ctx, link)

    @commands.command(name='play',
                      description='Bot will play a YouTube audio when it is NOT already in the voice channel. '
                                  '\nFormat: !play https://link.com')
    async def play(self, ctx, url: str):
        # check if the user is in a voice channel
        if ctx.author.voice:
            try:
                # connect to the voice channel
                channel = ctx.message.author.voice.channel
                if ctx.guild.id not in self.voice_clients:
                    voice_client = await channel.connect()
                    self.voice_clients[ctx.guild.id] = voice_client
                else:
                    voice_client = self.voice_clients[ctx.guild.id]

                # extract song information
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))
                song_url = data['url']
                player = discord.FFmpegOpusAudio(song_url, **self.ffmpeg_options)

                # play current song and then next in queue afterwards
                if not voice_client.is_playing():
                    voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx),
                                                                                               self.client.loop))

                    # Create an embed for the current song
                    embed = discord.Embed(
                        title='Now playing 🎧',
                        url=url,
                        description=f'{data["title"]}'
                    )
                    embed.set_author(
                        name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

                    # Fetch and set the thumbnail from the YouTube video
                    video_id = re.search(r"v=([^&]+)", url).group(1)
                    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                    embed.set_thumbnail(url=thumbnail_url)

                    await ctx.send(embed=embed)

                # If something is already playing, add the current song to the queue using the queue method
                else:
                    await self.queue(ctx, url)
            except Exception as e:
                print(f"An error occurred: {e}")
                await ctx.send("An error occurred while trying to play the song.")

        else:
            await ctx.send("You are not in a voice channel.")

    # clears current queue
    @commands.command(name='clear_queue',
                      description='Current queue is cleared.')
    async def clearQ(self, ctx):
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()
            await ctx.send('Queue cleared 🧹')
        else:
            await ctx.send('There is no queue to clear.')

    # pauses current song
    @commands.command(name='pause',
                      description='Current playing song will be paused')
    async def pause(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].pause()
            await ctx.send('Music has been paused ⏸️')
        except Exception as e:
            print(e)

    # resumes current song
    @commands.command(name='resume',
                      description='Current paused song will resume ▶️')
    async def resume(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(e)

    # ends jam session
    @commands.command(name='stop',
                      description='Current jam session will end ⏹️')
    async def stop(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].stop()
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]
            await ctx.send('You have ended your jam session.')
        except Exception as e:
            print(e)

    # adds song link into queue dictionary
    @commands.command(name='queue',
                      description='A song is added to the queue.'
                                  '\nFormat: !queue https://link.com')
    async def queue(self, ctx, link):
        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = []
        self.queues[ctx.guild.id].append(link)

        # extract video ID using regex
        video_id = re.search(r"v=([^&]+)", link)
        if video_id:
            video_id = video_id.group(1)
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        else:
            thumbnail_url = None

        # showing link & queue position
        embed = discord.Embed(
            title='Added to queue 🎶', url=link, description=f'Position: {len(self.queues[ctx.guild.id])}')

        # showing who queued
        embed.set_author(
            name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)

        # if youtube thumbnail URL is valid, set it in the embed
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        await ctx.send(embed=embed)


async def setup(client):
    await client.add_cog(Music(client))
