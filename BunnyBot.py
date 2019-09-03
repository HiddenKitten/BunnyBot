import asyncio
import discord 
from discord.ext import commands

VERSION = '1.03'




class Bot(commands.Bot):
    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = self.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await ctx.send(page)
        else:
            pages = await self.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)


bot = Bot("bb ", activity=discord.Game("Playing With My Food"))


@bot.event
async def on_command_error(ctx, error):
    """The event triggered when an error is raised while invoking a command.
    ctx   : Context
    error : Exception"""
    if hasattr(ctx.command, 'on_error'):
        return
    elif isinstance(error, commands.NoPrivateMessage):
        try:
            return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
        except:
            pass
    if isinstance(error, commands.MissingRequiredArgument):
        await bot.send_cmd_help(ctx)


async def is_owner(ctx):
    return ctx.author.id == 266079468135776258



@bot.event
async def on_ready():
    print('Connected Successfully! Bunny Bot Version %s' % VERSION)

@bot.command(name="ping")
async def _ping(ctx):
    """pong!"""
    await ctx.send("Pong! :ping_pong:")

@bot.command(name="version")
async def _version(ctx):
    """shows the version info"""
    await ctx.send("Version %s" % VERSION)

@bot.command(name="changelog")
async def _changelog(ctx):
    """view the changelog!"""
    with open('data/changelog.txt') as f:
        await ctx.send(f.read())

@bot.command(name="poll")
async def _poll(ctx, text, *options):
    """create a poll, limited to 10 options"""
    reactions = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
    message = text + '\n'
    options = list(options)
    if 'ping' in options:
        options.remove('ping')
        message = "@everyone " + message
    reactions = reactions[:len(options)] # needed done for later for adding the right reactions.
    for i in zip(reactions, options):
        message += "\n{0}: {1}".format(i[0], i[1])
    msg = await ctx.send(message)
    for i in reactions:
        await msg.add_reaction(i)

@commands.check(is_owner)
@bot.command(name="debug", hidden=True)
async def _debug(ctx, *, code):
    await ctx.send('```python\n'+eval(code)+'\n```')

@commands.has_role('BunnyBot Dev')
@bot.command(name='stop', hidden=True)
async def _stop(ctx):
    """shuts down the bot"""
    await ctx.send("Shutting Down.")
    await bot.logout()

if __name__ == '__main__':
    with open('.token', 'r') as f:
        __token = f.readline()
    bot.run(__token)
