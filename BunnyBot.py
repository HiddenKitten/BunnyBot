import asyncio
import discord
import typing
from discord.ext import commands
from datetime import datetime, timedelta

#static vars, read from config(s) later
OWNERS = [266079468135776258, 89032716896460800]
PATREON_EXT = 'MeeMTeam'

#Version, basically self tracking our updates
VERSION = 're-1.10'

bot = commands.Bot("bb ", activity=discord.Game(
    name="Playing with my food!"))

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
    elif isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send_help(ctx.command)
    elif isinstance(error, commands.CommandNotFound):
        return # ignore unfound commands for now. no reason to care, just would cause spam in console, or chat.
    print("command '{}' with args '{}' raised exception: '{}'".format(ctx.command, ctx.message.content[len(ctx.invoked_with)+len(ctx.prefix)+1:], error.original))

@bot.event
async def on_message(message):
    if 'order 66' in message.content.lower():
        await message.channel.send('It will be done, my Lord.')
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print('Connected Successfully! Bunny Bot Version %s' % VERSION)


# Checks


async def is_owner(ctx):
    return ctx.author.id in OWNERS


# Commands


@bot.command(name='avatar')
async def _avatar(ctx, member: typing.Optional[discord.Member]):
    """Get someone's Avatar!"""
    member = ctx.author if member is None else member
    em = discord.Embed(
        description='{0}, requested by:\n{1}'.format(member, ctx.author))
    em.set_thumbnail(url=member.avatar_url)
    await ctx.send(embed=em)


@bot.command(name="changelog", aliases=['changes'])
async def _changelog(ctx):
    """View the changelog!"""
    with open('data/changelog.txt') as f:
        await ctx.send(f.read())


@commands.check(is_owner)
@bot.command(name="debug", hidden=True)
async def _debug(ctx, *, code):
    """breaking rule #1 of Coding
    
    never trust user input.
    only anyone in the owners list can use this."""
    await ctx.send('```python\n'+exec(compile(code, "debug_command", 'exec'))+'\n```')


@bot.command(name="dice", aliases=["roll", 'rd'])
async def _dice(ctx, expression):
    """🎲 rolls dice expressions.
    
    6d20 will roll 6, 20-sided dice.

    some modifiers supported:
    6d20h3 will keep the 3 highest.
    6d20l3 will keep the 3 lowest.
    6d20r3 will reroll any 3s or lower *once*.
    6d20rr3 will reroll any 3s or lower, making the minimum roll 4.
    6d20a4 will count double for any 4s rolled.
    6d20e3 will count the number equal or above 3.
    6d20s will sort them lowest to highest.
    6d20+3 will add 3 to the total.
    6d20-3 will subtract 3 from the total.
    6d20.+3 will add 3 to every die.
    6d20.-3 winn subtract 3 from every die.
    """
    from dice import roll, DiceBaseException
    from re import search
    mod = '0'
    if search(r'[^\.]\+\d+$', expression):
        expression, mod = expression.split('+')
    elif search(r'[^\.]\-\d+$', expression):
        expression, mod = expression.split('-')
        mod = '-'+mod
    valmod = int(mod)
    try:
        a = roll(expression)
    except DiceBaseException as e:
        await ctx.send('Error in expression:\n```{}\n{}```'.format(expression, e.pretty_print()))
        return
    mod = '' if valmod is 0 else ', {:+d}'.format(valmod)
    if isinstance(a, list):
        if len(str(a)) <= 1000:
            message = '🎲 {}\ntotal 🎲 is {}'.format((', '.join(str(x) for x in a) + mod), sum(a, valmod))
        else:
            message = 'total 🎲 is {}'.format(sum(a, valmod))
    else:
        message = "total 🎲 is {} \nSince you added more dice after the +, I couldn't get you the list of individual dice rolls.".format(a)
    await ctx.send(message)


@bot.command(name="info")
async def _info(ctx, *, member: typing.Optional[discord.Member]):
    """Tells you some info about a member"""
    if member is None:
        member = ctx.author
    e = discord.Embed(title=member.display_name+"'s info", description="Heres what I could find!",
                      color=(member.top_role.colour if member.top_role.colour != 0 else 10070709))
    e.add_field(name='Name', value=member.name)
    e.add_field(name='User ID', value=member.id)
    e.add_field(name='Status', value=member.status)
    e.add_field(name='Highest Role', value=member.top_role)
    e.add_field(name='Join Date', value=member.joined_at)
    e.add_field(name='Registration Date', value=member.created_at)
    e.set_thumbnail(url=member.avatar_url)
    await ctx.send(embed=e)


@bot.command(name="ping")
async def _ping(ctx):
    """Pong!"""
    from time import time
    s = time()*10000
    m = await ctx.send("Ping! :ping_pong:")
    p = int(time()*10000 - s)/10.0
    await m.edit(content="Pong, {}ms! :ping_pong: ".format(p))
    


@bot.command(name="poll")
async def _poll(ctx, text, *options):
    """Create a poll, limited to 10 options. currently kinda broken"""
    reactions = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
    message = text + '\n'
    options = list(options)
    # # old ping code, re add later if needed? 
    # # this could have been abused by anyone for a while lol
    # if 'ping' in options:
    #     options.remove('ping')
    #     message = "@everyone " + message
    # # needed done for later for adding the right reactions.
    reactions = reactions[:len(options)]
    for i in zip(reactions, options):
        message += "\n{0}: {1}".format(i[0], i[1])
    msg = await ctx.send(message)
    for i in reactions:
        await msg.add_reaction(i)


@commands.has_role('BunnyDev')
@bot.command(name='stop', hidden=True, aliases=['shutdown'])
async def _stop(ctx):
    """Shuts down the bot"""
    await ctx.send("Shutting Down...")
    await bot.logout()

@bot.command(name="serverinfo", aliases=['si'])
async def _serverinfo(ctx):
    """shows the guilds info"""
    guild = ctx.guild
    e = discord.Embed(title=guild.name+"'s info", description="Heres what I could find!")
    e.add_field(name="Guild Name", value=guild.name)
    e.add_field(name="Guild Server Location", value=guild.region)
    e.add_field(name="Members", value=guild.member_count)
    e.add_field(name="Owner", value=guild.owner)
    e.add_field(name="Created At", value=guild.created_at)
    e.set_thumbnail(url=guild.icon_url)
    await ctx.send(embed=e)

@bot.command(name="version", aliases=['ver'])
async def _version(ctx):
    """shows the version info"""
    await ctx.send("Version " + VERSION)

@bot.command(name="patreon")
async def _patreon(ctx):
    """sends patreon link"""
    await ctx.send("I'm glad you're thinking of supporting our work!\nhttps://www.patreon.com/" + PATREON_EXT)

@commands.has_permissions(manage_messages=True)
@bot.command(name="clean")
async def _clean(ctx, last: int, user: typing.Optional[discord.Member], after: typing.Optional[discord.Message], before: typing.Optional[discord.Message]):
    """cleans up messages.
    
    last: the last x messages to check. 
    user: the user to delete.
    after: after a specific message, specified by id.
    before: before a specific message, specified by id.
    note: bulk_delete on the api is limited to the last 14 days, regardless of input here."""


    messages = await ctx.channel.history(limit=last, before=before, after=after).flatten()
    def filter_function(x):
        return x.created_at > (datetime.now() - timedelta(days=14)) and (x.author == user) if user else True
    messages = list(filter(filter_function, messages))
    chunks = [messages[x:x+100] for x in range(0, len(messages), 100)]
    for i in chunks:
        await ctx.channel.delete_messages(i)
    await ctx.message.delete(delay=5)

# Internals

# Error Handling

# @_info.error # obsolete error code.
# async def _info_error(ctx, error):
#     if isinstance(error, commands.BadArgument):
#         await ctx.send('I could not find that member...')


# Running

if __name__ == '__main__':
    with open('.token', 'r') as f:
        __token = f.readline()
    bot.run(__token)
