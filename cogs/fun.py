import discord
import typing
from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if 'order 66' in message.content.lower():
            await message.channel.send('It will be done, my Lord.')


    @commands.command(name="dice", aliases=["roll", 'rd'])
    async def _dice(self, ctx, expression):
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

    @commands.command(name='avatar')
    async def _avatar(self, ctx, member: typing.Optional[discord.Member]):
        """Get someone's Avatar!"""
        member = ctx.author if member is None else member
        em = discord.Embed(
            description='{0}, requested by:\n{1}'.format(member, ctx.author))
        em.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=em)



def setup(bot):
    bot.add_cog(Fun(bot))