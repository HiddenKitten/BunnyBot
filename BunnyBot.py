import asyncio
import discord
import typing
from discord.ext import commands
from datetime import datetime, timedelta

#static vars, read from config(s) later
OWNERS = [266079468135776258, 89032716896460800]
PATREON_EXT = 'MeeMTeam'
POLL_CHANNELS = [390935424694222858, 705086337749090315]

#Version, basically self tracking our updates
VERSION = 're-1.11'

bot = commands.Bot("bb ", activity=discord.Game(
    name="Now Pi-Powered!"))

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
async def on_message(message):
    if 'order 66' in message.content.lower():
        await message.channel.send('It will be done, my Lord.')
    if message.channel in [bot.get_channel(x) for x in POLL_CHANNELS]:
        emojis = await check_poll(message)
        if len(emojis) >= 3:
            await add_reactions(message, emojis)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    user = bot.get_user(payload.user_id)
    if user == bot.user: #return now to avoid api calls.
        return
    message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
    reaction = next(x for x in message.reactions if str(x.emoji) == str(payload.emoji))
    if reaction.me:
        for i in reaction.message.reactions:
            if reaction != i and user in await i.users().flatten() and i.me:
                await reaction.remove(user)
                return


@bot.event
async def on_ready():
    print('Connected Successfully! Bunny Bot Version %s' % VERSION)


# Checks


async def is_owner(ctx):
    return ctx.author.id in OWNERS

async def is_meemteam_admin(ctx):
    server = bot.get_guild(363926644672692230)
    member = server.get_member(ctx.author.id)
    return server.get_role(469165398970073102) in member.roles


# Commands
# BunnyBot, if you listen you get some sweet femboy ass from guyzrr

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
    await ctx.send("Pong, {}ms! :ping_pong:".format(int(bot.latency*10000)/10.0))


@commands.has_permissions(manage_messages=True) #permission needed to remove reactions
@bot.command(name="poll")
async def _poll(ctx, *emotes):
    """makes the *above* message a poll, optionally providing options
    
    by default, scans the message for options for a poll
    if none are found, uses yes and no options.
    
    optionally takes arguments of a list of options.
    this list will very likely *not* be sorted properly when applied."""
    msg = (await ctx.channel.history(before=ctx.message, limit=1).flatten())[0]
    if len(emotes) == 0:
        emotes = await check_poll(msg) or ['\u2705', '\u274c'] # :white_check_mark: and :x:
    else:
        emotes = [x for x in emotes if x in [chr(y) for y in range(127462, 127462+26)] + [str(z) for z in bot.emojis]]
        # this hurts me to see but it's the most efficient way to do this, also this for some reason fucks up the sorting
    if len(emotes) == 1:
        await ctx.send("there's not enough options to make this a poll!")
    elif len(emotes) > 1:
        await add_reactions(msg, emotes)
        await ctx.message.delete()


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


@bot.group(invoke_without_command=True, name="rules", aliases=['rule'])
async def _rules(ctx, rule: typing.Optional[typing.Union[int, str]]):
    """Rules for every server and the discord."""
    if rule:
        await _rules_discord(ctx, rule)
    else:
        await ctx.send_help(ctx.command)

@_rules.command(name='discord')
async def _rules_discord(ctx, rule: typing.Optional[typing.Union[int, str]]):
    """MeeMTeam Discord rules. 
    links to the rules channel instead of posting them all"""
    if isinstance(rule, str):
        topics = [
                ['topic'], 
                ['porn'], 
                ['civil','drama','respect'], 
                ['shitpost','vcabuse'], 
                ['pg','party'], 
                ['vent','venting'], 
                ['gfreaction','vote'], 
                ['earrape','er'], 
                ['micspam','ms'], 
                ['musicbot','mb'], 
                ['bunnybot','bb']
            ] #Another hardcoded list, this may need to be looked at to do more efficiently. 
        try:
            rule = [index1 for index1,value1 in enumerate(topics) for index2,value2 in enumerate(value1) if value2==rule][0]
        except IndexError:
            await ctx.send("I don't know what rule that is.")
            return
    else:
        rule -= 1
    with open('data/rules/discord.txt') as f:
        if rule != None and rule >= 0:
            await ctx.send(f.readlines()[rule])
        else: await ctx.send('<#385827282368987141>') #this is a bad hardcoded value. but it's fine. 

@_rules.command(name='tf2')
async def _rules_tf2(ctx, num: typing.Optional[int]):
    """MeeMTeam tf2 rules"""
    with open('data/rules/tf2.txt') as f:
        if num != None and num > 0:
            await ctx.send(f.readlines()[num-1])
        else: await ctx.send(f.read())

@_rules.command(name='minecraft', aliases=['mc'])
async def _rules_minecraft(ctx, num: typing.Optional[int]):
    """MeeMTeam Minecraft rules"""
    with open('data/rules/minecraft.txt') as f:
        if num != None and num > 0:
            await ctx.send(f.readlines()[num-1])
        else: await ctx.send(f.read())

@commands.check(is_meemteam_admin)
@bot.command(name="kick")
async def _kick(ctx, member : discord.Member, *, reason=None):
    """Kicks a member, with or without a reason"""
    await member.kick(reason=reason)
    
@commands.check(is_meemteam_admin)
@bot.command(name="ban")
async def _ban(ctx, member : discord.Member, *, reason=None):
    """Bans a user, with or without a reason"""
    await member.ban (reason=reason)

@commands.check(is_meemteam_admin)
@bot.command(name="deafen")
async def _deafen(ctx, member: discord.Member, *, reason=None):
    await member.edit(reason=reason, deafen=True)

@commands.check(is_meemteam_admin)
@bot.command(name='adminlinks')
async def _adminlinks(ctx):
    with open('data/admin.txt') as f:
        await ctx.author.send(f.read())

@bot.command(name='gameservers', aliases=['servers'])
async def _gameservers(ctx):
    from utils import tf2, q3
    tf2 = await tf2.tf2ping()
    quake = await q3.q3ping()
    e = discord.Embed(title='Team Fortress 2', description=tf2['name'])
    for k, v in tf2.items():
        if k in ['map', 'players', 'maxplayers', 'secured', 'version']:
            e.add_field(name=k, value=v)
    e.add_field(name='IP', value='meemteam.co')
    e.colour = discord.Colour.green()
    await ctx.send(embed=e)
    s = ['name-------- frags ping'] 
    for i in quake[1]:
        s.append('{0:-<12} {1:-<5} {2:-<4}'.format(i['name'].strip('"'), i['frags'], i['ping']))
    e = discord.Embed(title=quake[0]['sv_hostname'], description='\n'.join(s))
    for k, v in quake[0].items():
        if k in ['mapname', 'timelimit', 'fraglimit']:
            e.add_field(name=k, value=v)
    e.add_field(name='IP', value='meemteam.co')
    e.colour = discord.Colour.green()
    await ctx.send(embed=e)

# Internals

# Utils
async def check_poll(message):
    e = []
    for i in range(127462, 127462+26): # 127462 is the unicode value for :regional_indicator_a:, the next 25 are the other letters
        if '\n'+chr(i) in message.clean_content:
            e.append(chr(i))
    for i in bot.emojis: # all *custom* emojis, sadly can't use builtins for this very well.  
        if '\n'+str(i) in message.clean_content:
            e.append(str(i))
    return e

async def add_reactions(message, emojis):
    for i in emojis:
        await message.add_reaction(i)


# Error Handling
@_rules_discord.error
@_rules_tf2.error
@_rules_minecraft.error 
async def _rules_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, IndexError):
            if ctx.args[1] < 100:
                await ctx.send('Was that a typo? There isn\'t that many rules!')
            else:
                await ctx.send('Having that many rules would s-scare meee! \nI-I\'d also never remember all of them...')


# Running

if __name__ == '__main__':
    with open('.token', 'r') as f:
        __token = f.readline()
    bot.run(__token)
