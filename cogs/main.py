import asyncio
import discord
import typing
import json
from discord.ext import commands, tasks
from datetime import datetime, timedelta

# predicates
async def is_owner(ctx):
    return ctx.author.id in ctx.bot.cfg["owners"]

class Main(commands.Cog, name="BunnyBot"):

    def __init__(self, bot):
        self.bot = bot
        self._rules.enabled = bot.cfg['rules']
        self._ip.enabled=bot.cfg['ips']

    @commands.command(name="changelog", aliases=['changes'])
    async def _changelog(self, ctx):
        """View the changelog!"""
        with open('data/changelog.txt') as f:
            await ctx.send(f.read())

    @commands.check(is_owner)
    @commands.command(name="debug", hidden=True)
    async def _debug(self, ctx, *, code):
        """breaking rule #1 of Coding

        never trust user input.
        only anyone in the owners list can use this."""
        await ctx.send('```python\n'+exec(compile(code, "debug_command", 'exec'))+'\n```')

    @commands.command(name="patreon")
    async def _patreon(self, ctx):
        """sends patreon link"""
        await ctx.send("I'm glad you're thinking of supporting our work!\nhttps://www.patreon.com/" + ctx.bot.cfg["patreon_ext"])

    @commands.has_permissions(manage_messages=True)
    @commands.command(name="clean")
    async def _clean(self, ctx, last: int, user: typing.Optional[discord.Member], after: typing.Optional[discord.Message], before: typing.Optional[discord.Message]):
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

    @commands.command(name="info")
    async def _info(self, ctx, *, member: typing.Optional[discord.Member]):
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

    @commands.has_permissions(kick_members=True)
    @commands.command(name="kick")
    async def _kick(self, ctx, member : discord.Member, *, reason=None):
        """Kicks a member, with or without a reason"""
        await member.kick(reason=reason)

    @commands.has_permissions(ban_members=True)
    @commands.command(name="ban")
    async def _ban(self, ctx, member : discord.Member, *, reason=None):
        """Bans a user, with or without a reason"""
        await member.ban (reason=reason)

    @commands.has_permissions(deafen_members=True)
    @commands.command(name="deafen")
    async def _deafen(self, ctx, member: discord.Member, *, reason=None):
        await member.edit(reason=reason, deafen=True)

    @commands.command(name="ping")
    async def _ping(self, ctx):
        """Pong!"""
        await ctx.send("Pong, {}ms! :ping_pong:".format(int(self.bot.latency*10000)/10.0))

    @commands.has_role('BunnyDev')
    @commands.command(name='shutdown', hidden=True)
    async def _shutdown(self, ctx):
        """Shuts down the bot"""
        await ctx.send("Shutting Down...")
        await self.bot.logout()

    @commands.command(name="serverinfo", aliases=['si'])
    async def _serverinfo(self, ctx):
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

    @commands.command(name="version", aliases=['ver'])
    async def _version(self, ctx):
        """shows the version info"""
        await ctx.send("Version " + self.bot.VERSION)

    @commands.command(name="ip")
    async def _ip(self, ctx):
        """Sends all the ways to connect to our servers!"""
        e = discord.Embed(title="MeeMTeam Servers!", description="How to connect to our servers!")
        e.add_field(name="TF2", value="click this: steam://connect/meemteam.co\nor open the console, type `connect meemteam.co`")
        e.add_field(name="Minecraft", value="Add server, address is `meemteam.co`")
        e.add_field(name="Quake", value="'specify', meemteam.co with the default port")
        e.add_field(name="Anything else", value="in general, the steps are just connect to `meemteam.co`, however you would any other server. If you need help, then ping the adminstrator role, one of us will be able to help you!")
        await ctx.send(embed=e)


    @commands.group(invoke_without_command=True, name="rules", aliases=['rule'])
    async def _rules(self, ctx, rule: typing.Optional[typing.Union[int, str]]):
        """Rules for our servers and the discord."""
        if rule:
            await self._rules_discord(ctx, rule)
        else:
            await ctx.send_help(ctx.command)

    @_rules.command(name='discord')
    async def _rules_discord(self, ctx, rule: typing.Optional[typing.Union[int, str]]):
        """Discord server rules.
        links to the rules channel instead of posting them all"""
        if isinstance(rule, str):
            topics = [
                    ['topic'],
                    ['porn'],
                    ['civil','drama','respect'],
                    ['shitpost','vcabuse'],
                    ['pg','party'],
                    ['vent','venting'],
                    ['earrape','er'],
                    ['micspam','ms'],
                    ['musicbot','mb'],
                    ['bunnybot','bb']
                ]
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
            else: await ctx.send('<#385827282368987141>')

    @_rules.command(name='tf2')
    async def _rules_tf2(self, ctx, num: typing.Optional[int]):
        """tf2 server rules"""
        with open('data/rules/tf2.txt') as f:
            if num != None and num > 0:
                await ctx.send(f.readlines()[num-1])
            else: await ctx.send(f.read())

    @_rules.command(name='minecraft', aliases=['mc'])
    async def _rules_minecraft(self, ctx, num: typing.Optional[int]):
        """Minecraft server rules"""
        with open('data/rules/minecraft.txt') as f:
            if num != None and num > 0:
                await ctx.send(f.readlines()[num-1])
            else: await ctx.send(f.read())

    # Error Handling
    @_rules_discord.error
    @_rules_tf2.error
    @_rules_minecraft.error
    async def _rules_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, IndexError):
                if ctx.args[1] < 100:
                    await ctx.send('Was that a typo? There isn\'t that many rules!')
                else:
                    await ctx.send('Having that many rules would s-scare meee! \nI-I\'d also never remember all of them...')

    #always loop
    @tasks.loop(seconds=15.0)
    async def _random_status(self):
        if self.bot.cfg['rnd_status']:
            from random import choice
            a = discord.Game(choice(self.bot.cfg["statuses"]).format(prefix=self.bot.cfg["prefix"]))
            await self.bot.change_presence(activity=a, status=discord.Status.online)

    @_random_status.before_loop
    async def _before_loops(self):
        await self.bot.wait_until_ready()

def setup(bot):
    n = Main(bot)
    n._random_status.start() # pylint: disable=no-member
    bot.add_cog(n)
