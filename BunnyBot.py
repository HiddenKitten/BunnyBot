import asyncio
import discord
import typing
import logging
from discord.ext import commands
from datetime import datetime




load_on_startup = ["main", "fun", "polls"]

#enable the logger as discord's default.

logging.basicConfig(level=logging.INFO)

try:
    import os
    os.mkdir('logs', 751)
except FileExistsError:
    pass

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='logs/{date:%Y-%m-%d_%H-%M-%S}.log'.format( date=datetime.now() ), encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot("bb ", activity=discord.Game(
    name="Modularized!"))

#Version, basically self tracking our updates
bot.VERSION = 'md-1.13'

# Events
@bot.event
async def on_command_error(ctx, error):
    """The event triggered when an error is raised while invoking a command.
    ctx   : Context
    error : Exception"""
    # if hasattr(ctx.command, 'on_error'): # whatever. this is fine. 
    #     return
    if isinstance(error, commands.NoPrivateMessage):
        try:
            return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except:
            pass
    elif isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send_help(ctx.command)
    elif isinstance(error, commands.CommandNotFound):
        return # ignore unfound commands for now. no reason to care, just would cause spam in console, or chat.
    print("command '{}' with args '{}' raised exception: '{}'".format(ctx.command, ctx.message.content[len(ctx.invoked_with)+len(ctx.prefix)+1:], error))

@bot.event
async def on_ready():
    print('Connected Successfully! Bunny Bot Version %s' % bot.VERSION)



# Server Specific Commands

@bot.command(name="ip")
async def _ip(ctx):
    """Sends all the ways to connect to our servers!"""
    e = discord.Embed(title="MeeMTeam Servers!", description="How to connect to our servers!")
    e.add_field(name="TF2", value="click this: steam://connect/meemteam.co\nor open the console, type `connect meemteam.co`")
    e.add_field(name="Minecraft", value="Add server, address is `meemteam.co`")
    e.add_field(name="Quake", value="'specify', meemteam.co with the default port")
    e.add_field(name="Anything else", value="in general, the steps are just connect to `meemteam.co`, however you would any other server. If you need help, then ping the adminstrator role, one of us will be able to help you!")
    await ctx.send(embed=e)

# Running

if __name__ == '__main__':
    for extension in load_on_startup:
        try:
            bot.load_extension("cogs."+extension)
        except Exception as e:
            print('Failed to load extension {extension}.')
            raise e
    with open('.token', 'r') as f:
        __token = f.readline()
    bot.run(__token)
