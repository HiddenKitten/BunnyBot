import asyncio
import discord
import typing
import json
from discord.ext import commands

class Polls(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        with open("data/private/polls.json") as f:
            self.poll_cfg = json.load(f)
    #utils

    async def check_poll(self, message):
        e = []
        for i in range(127462, 127462+26): # 127462 is the unicode value for :regional_indicator_a:, the next 25 are the other letters
            if '\n'+chr(i) in message.clean_content:
                e.append(chr(i))
        for i in self.bot.emojis: # all *custom* emojis, sadly can't use builtins for this very well.
            if '\n'+str(i) in message.clean_content:
                e.append(str(i))
        return e

    async def add_reactions(self, message, emojis):
        for i in emojis:
            await message.add_reaction(i)

    #Listener
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel in [self.bot.get_channel(x) for x in self.poll_cfg["Poll_Channels"]]:
            emojis = await self.check_poll(message)
            if len(emojis) >= 3:
                await self.add_reactions(message, emojis)
    #commands
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        user = self.bot.get_user(payload.user_id)
        if user == self.bot.user: #return now to avoid api calls.
            return
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        reaction = next(x for x in message.reactions if str(x.emoji) == str(payload.emoji))
        if reaction.me:
            for i in reaction.message.reactions:
                if reaction != i and user in await i.users().flatten() and i.me:
                    await reaction.remove(user)
                    return


    @commands.has_permissions(manage_messages=True) #permission needed to remove reactions
    @commands.command(name="poll")
    async def _poll(self, ctx, *emotes):
        """makes the *above* message a poll, optionally providing options

        by default, scans the message for options for a poll
        if none are found, uses yes and no options.

        optionally takes arguments of a list of options.
        this list will very likely *not* be sorted properly when applied."""
        msg = (await ctx.channel.history(before=ctx.message, limit=1).flatten())[0]
        if len(emotes) == 0:
            emotes = await self.check_poll(msg) or ['\u2705', '\u274c'] # :white_check_mark: and :x:
        else:
            emotes = [x for x in emotes if x in [chr(y) for y in range(127462, 127462+26)] + [str(z) for z in self.bot.emojis]]
            # this hurts me to see but it's the most efficient way to do this, also this for some reason fucks up the sorting
        if len(emotes) == 1:
            await ctx.send("there's not enough options to make this a poll!")
        elif len(emotes) > 1:
            await self.add_reactions(msg, emotes)
            await ctx.message.delete()



def setup(bot):
    bot.add_cog(Polls(bot))