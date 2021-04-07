import discord
import logging
import json
from discord.ext import commands
from datetime import datetime

#enable the logger as discord's default.
logging.basicConfig(level=logging.INFO)

try:
    import os
    os.mkdir('logs', 751)
except FileExistsError:
    pass

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

with open("data/bot.json") as f:
    cfg = json.load(f)
bot = commands.Bot(cfg['prefix'], activity=discord.Game(
    name="Modularized!"))

if cfg['log_to_file']:
    handler = logging.FileHandler(filename='logs/{date:%Y-%m-%d_%H-%M-%S}.log'.format( date=datetime.now() ), encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    handler2 = logging.FileHandler(filename='logs/latest.log', encoding='utf-8', mode='w')
    handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    logger.addHandler(handler2)

bot.cfg=cfg
bot.logger = logger.getChild('bunny')

bot.VERSION = 'md-1.15'

# Events
@bot.event
async def on_command_error(ctx, error):
    """The event triggered when an error is raised while invoking a command.
    ctx   : Context
    error : Exception"""
    if isinstance(error, commands.NoPrivateMessage):
        try:
            return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except:
            pass
    elif isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send_help(ctx.command)
    elif isinstance(error, commands.CommandNotFound):
        return
    ctx.bot.logger.error("command '{}' with args '{}' raised exception: '{}'".format(ctx.command, ctx.message.content[len(ctx.invoked_with)+len(ctx.prefix)+1:], error))

@bot.event
async def on_ready():
    bot.logger.info('Connected Successfully! Bunny Bot Version %s' % bot.VERSION)

# Running

if __name__ == '__main__':
    for extension in set(["main"]+cfg["startup_cogs"]): #always load the "main" cog, ignore duplicates using set.
        try:
            bot.load_extension("cogs."+extension)
        except Exception as e:
            print('Failed to load extension {extension}.')
            raise e
    bot.run(cfg.pop("token"))
