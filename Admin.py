import discord
from discord.ext import commands  # importing commands from discord extension
from dotenv import load_dotenv
from discord.ext.commands import has_permissions, MissingPermissions
from discord.utils import get

load_dotenv()


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    # kicks out wanted member
    @commands.command(name='kick',
                      description='Bot will remove the member if the caller has the correct perms.'
                                  '\nFormat: !kick @username')
    @has_permissions(kick_members=True)  # makes sure user with the correct role can kick, not just anyone in the server
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f'User {member} has been kicked')

    # shows if someone tries to kick without proper perms
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to kick people 🙅‍♀️")

    # bans wanted member
    @commands.command(name='ban',
                      description='Bot will ban the member if the caller has the correct perms.'
                                  '\nFormat: !ban @username')
    @has_permissions(ban_members=True)  # makes sure user with the correct role can ban, not just anyone in the server
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f'User {member} has been banned 🚫')

    # shows if someone tries to ban without proper perms
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to ban people 🙅‍♀️")

    # unbanning a banned member
    @commands.command(description='Bot will unban the member.'
                                  '\nFormat: !unban @username')
    @has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_id: int):
        bans = [entry async for entry in ctx.guild.bans(limit=2000)]
        for ban_entry in bans:
            user = ban_entry.user
            if user.id == member_id:
                await ctx.guild.unban(user)
                await ctx.send(f'User {user} has been unbanned.')
                return
            else:
                await ctx.send(f'User with ID {member_id} is not currently banned.')

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to run this command 🙅‍♀️")

    # embed example, do cooler stuff with it later!
    # discord url's require starting with 'https'
    @commands.command(description='An embed is displayed.')
    async def feedback(self, ctx):
        # embed author + author 
        embed = discord.Embed(title='Feedback Form Link',
                              url='https://forms.gle/1Vy6EVVVKamoajiY9',
                              description='Feel free to share any thoughts, complaints, or wishes ✍️',
                              color=0x4dff4d)

        # load the uploaded image file for thumbnail
        file_path = '/Users/victoria4318/Documents/DiscordBotProject/cogs/feedback_icon.png'
        file = discord.File(file_path, filename='feedback_icon.png')
        embed.set_thumbnail(url=f'attachment://{file.filename}')

        embed.set_footer(text='All information is collected anonymously 🤫 and greatly appreciated ❤️')

        await ctx.send(embed=embed, file=file)

    # perms error handling
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to run this command 🙅‍♀️")

    # adds roles if member doesn't already have it
    @commands.command(pass_context=True,
                      description='Said role is added to the member.'
                                  '\nFormat: !addRole @username role name')
    @commands.has_permissions(manage_roles=True)
    async def addRole(self, ctx, user: discord.Member, *, role: discord.Role):
        if role in user.roles:
            await ctx.send(f"{user.mention} already has the role, {role}")
        else:
            await user.add_roles(role)
            await ctx.send(f"Added {role} to {user.mention}")

    @addRole.error
    async def addRole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have permission to use this command 🙅‍♀️')

    # removes roles
    @commands.command(pass_context=True,
                      description='Said role is removed from the member.'
                                  '\nFormat: !removeRole @username role name')
    @commands.has_permissions(manage_roles=True)
    async def removeRole(self, ctx, user: discord.Member, *, role: discord.Role):
        if role in user.roles:
            await user.remove_roles(role)
            await ctx.send(f"Removed {role} from {user.mention}")
        else:
            await ctx.send(f"{user.mention} does not have the role, {role}")

    @removeRole.error
    async def removeRole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have permission to use this command 🙅‍♀️')

    @commands.command(name='server_stats', description='Displays server statistics.')
    async def server_stats(self, ctx):
        guild = ctx.guild  # Get the guild (server) object
        member_count = guild.member_count  # Total number of members
        channel_count = len(guild.channels) - 2  # Total number of channels
        role_count = len(guild.roles) - 1  # Total number of roles

        # Create an embed to display the stats
        embed = discord.Embed(title=f"{guild.name} Server Stats", color=discord.Color.green())
        file_path = '/Users/victoria4318/Documents/DiscordBotProject/cogs/stats.jpeg'
        file = discord.File(file_path, filename='stats.jpeg')
        embed.set_thumbnail(url=f'attachment://{file.filename}')
        embed.add_field(name="Total Members", value=member_count, inline=True)
        embed.add_field(name="Total Channels", value=channel_count, inline=True)
        embed.add_field(name="Total Roles", value=role_count, inline=True)

        await ctx.send(embed=embed, file=file)


async def setup(client):
    await client.add_cog(Admin(client))
