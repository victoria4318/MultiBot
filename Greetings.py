import discord
from discord.ext import commands
import random

class Greetings(commands.Cog):

    def __init__(self, client):
        self.client = client

    # COMMAND in cogs uses @commands.command() instead of @client.command()
    @commands.command(name='hello', 
                      description='Bot greets the user.') # Bot sends a random greeting
    async def hello(self, ctx): # ctx allows you to communicate with your discord server (send/receive messages)
        greetings=[
            "Hello! 👋",
            "Hi there! 😊",
            "Hey! 🙌",
            "Greetings! 👋",
            "What's up? 😎",
            "Howdy! 🤠",
            "Hi! 👋",
            "Hey there! 🙋‍♂️",
            "Good to see you! 😃"]
        greeting = random.choice(greetings)

        await ctx.send(greeting)
    
    # EVENT in cogs uses @commands.Cog.listener() instead of @client.event()
    @commands.Cog.listener()
    async def on_member_join(self, member): # action when a member joins the server

        embed = discord.Embed(title = "What's up!👋", description = "👉To see what I can do type !help")
        file_path = '/Users/victoria4318/Documents/DiscordBotProject/cogs/multibot_icon.jpg'
        file = discord.File(file_path, filename = 'multibot_icon.jpg')
        embed.set_thumbnail(url=f'attachment://{file.filename}')
        
        await self.send(embed=embed, file=file)

    @commands.Cog.listener()
    async def on_member_remove(self, member): # action when a member leaves the server
        channel = self.client.get_channel(1219835278424936461)
        await channel.send("Leaving so soon? 😢 We'll miss you...")

    # bot notifies channel when someone adds a reaction to a message
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        channel = reaction.message.channel
        await channel.send(user.name + " added: " + reaction.emoji)

    # bot notifies channel when someone removes a reaction to a message
    # could be  used when changing roles
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        channel = reaction.message.channel
        await channel.send(user.name + " removed: " + reaction.emoji)

    # bot pins messages
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        
        if ('pin') in message.content:
            # emoji unicode from https://www.unicode.org/emoji/charts/full-emoji-list.html
            # instead of example: U+1F601 make the + 3 0's
            emoji = '\U0001F4CD'
            await message.channel.send('Message pinned!')
            await message.add_reaction(emoji)

    # dm from bot by calling !message @username
    @commands.command(description = 'A member can poke (ping) another user privately.' 
                      '\nFormat: !message @username')
    async def poke(self, ctx, user:discord.Member, *, message=None):
        message = "Someone poked you! 👉"
        embed = discord.Embed(title=message, 
                              description=f'{ctx.author.mention} wants you to look in the chat 👀')
        await user.send(embed=embed)

async def setup(client):
    await client.add_cog(Greetings(client))