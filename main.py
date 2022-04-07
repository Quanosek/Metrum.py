# start
import discord
from discord.ext import commands
from server import Website
import os

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())
client.remove_command('help')


# on ready
@client.event
async def on_ready():

    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name='!help'))

    print(' * Successfully logged in!')


# błędne komendy
@client.event
async def on_command_error(ctx, error):
    await ctx.message.add_reaction('❌')


# import cogs
from commands import commands
from music import music


async def setup():
    await client.wait_until_ready()
    client.add_cog(commands(client))
    client.add_cog(music(client))


# end

client.loop.create_task(setup())

Website()
client.run(os.environ['TOKEN'])
