import discord
# import json
from discord.ext import commands
 
class Polls(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # with open("data/private/gameservers.json") as f: 
        #     self.poll_cfg = json.load(f)
    #utils

    #commands
    @commands.group(invoke_without_command=True, name='gameservers', aliases=['servers'])
    async def _gameservers(self, ctx):
        """ping our servers, see if anyone's online!"""
        await ctx.send_help(ctx.command)

    @_gameservers.command(name='all')
    async def _all(self, ctx):
        await self._tf2(ctx)
        await self._quake(ctx)

    @_gameservers.command(name='tf2')
    async def _tf2(self, ctx):
        from utils import tf2
        tf2 = await tf2.tf2ping()
        e = discord.Embed(title='Team Fortress 2', description=tf2['name'])
        for k, v in tf2.items():
            if k in ['map', 'players', 'maxplayers', 'secured', 'version']:
                e.add_field(name=k, value=v)
        e.add_field(name='IP', value='meemteam.co')
        e.colour = discord.Colour.green()
        await ctx.send(embed=e)

    @_gameservers.command(name='quake3', aliases=['quake', 'q3'])
    async def _quake(self, ctx):
        from utils import q3
        quake = await q3.q3ping()
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