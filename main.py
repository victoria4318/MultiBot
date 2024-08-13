import discord
from discord.ext import commands
import os
from apikeys import *
import asyncio

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():  # not shown to user just tells creator that bot is ready and loaded to use
    # bot status
    await client.change_presence(status=discord.Status.online,
                                 activity=discord.Activity(type=discord.ActivityType.listening, name='Signal'))

    print("The bot is now ready for use!")
    print("-----------------------------")


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await client.load_extension(f"cogs.{filename[:-3]}")


async def main():
    async with client:
        await load()
        await client.start(BOTTOKEN)


asyncio.run(main())
