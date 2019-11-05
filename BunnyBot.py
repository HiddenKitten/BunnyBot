import asyncio
import random
import discord
import typing
from discord.ext import commands

VERSION = '1.07 indev'


bot = commands.Bot("bb ", activity=discord.Game(
    name="Telling Syko to Stop Eating Coins"))

# Events
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
        await bot.help_command.send_command_help(ctx.command)


@bot.event
async def on_ready():
    print('Connected Successfully! Bunny Bot Version %s' % VERSION)


# Checks


async def is_owner(ctx):
    return ctx.author.id == 266079468135776258


# Commands


@bot.command(name="age")
async def _age(ctx, *, user: discord.User):
    await ctx.send(user.created_at)


@bot.command(name='avatar')
async def _avatar(ctx, *, member: discord.Member):
    member = ctx.author if member is None else member
    em = discord.Embed(
        description='{0}, requested by:\n{1}'.format(member, ctx.author))
    em.set_thumbnail(url=member.avatar_url)
    await ctx.send(embed=em)


@bot.command(name="changelog")
async def _changelog(ctx):
    """view the changelog!"""
    with open('data/changelog.txt') as f:
        await ctx.send(f.read())


@commands.check(is_owner)
@bot.command(name="debug", hidden=True)
async def _debug(ctx, *, code):
    await ctx.send('```python\n'+eval(code)+'\n```')


@bot.command(name="dice")
async def _dice(ctx, number: typing.Optional[int] = 6):
    """roll a die"""
    arg = random.randint(1, number)
    await ctx.send(arg)


@bot.command(name="info")
async def _info(ctx, *, member: typing.Optional[discord.Member]):
    """Tells you some info about the member"""
    if member is None:
        member = ctx.author
    name = member.display_name
    uid = member.id
    status = member.status
    joined = member.joined_at
    highrole = member.top_role
    e = discord.Embed(title=name+"'s info", description="Heres what I could find!",
                      color=(highrole.colour if highrole.colour.value != 0 else 10070709))
    e.add_field(name='Name', value=name)
    e.add_field(name='User ID', value=uid)
    e.add_field(name='Status', value=status)
    e.add_field(name='Highest Role', value=highrole)
    e.add_field(name='Join Date', value=joined)
    await ctx.send(embed=e)


@bot.command(name="ping")
async def _ping(ctx):
    """pong!"""
    await ctx.send("Pong! :ping_pong:")


@bot.command(name="poll")
async def _poll(ctx, text, *options):
    """create a poll, limited to 10 options"""
    reactions = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
    message = text + '\n'
    options = list(options)
    if 'ping' in options:
        options.remove('ping')
        message = "@everyone " + message
    # needed done for later for adding the right reactions.
    reactions = reactions[:len(options)]
    for i in zip(reactions, options):
        message += "\n{0}: {1}".format(i[0], i[1])
    msg = await ctx.send(message)
    for i in reactions:
        await msg.add_reaction(i)


@commands.has_role('BunnyDev')
@bot.command(name='stop', hidden=True)
async def _stop(ctx):
    """shuts down the bot"""
    await ctx.send("Shutting Down.")
    await bot.logout()


@bot.command(name="version")
async def _version(ctx):
    """shows the version info"""
    await ctx.send("Version %s" % VERSION)


# Internals

# Error Handling


@_info.error
async def _info_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send('I could not find that member...')


# Running

if __name__ == '__main__':
    with open('.token', 'r') as f:
        __token = f.readline()
    bot.run(__token)
