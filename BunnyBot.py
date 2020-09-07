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
