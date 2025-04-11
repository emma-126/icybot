import tracemalloc
import logging

import asyncio
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

tracemalloc.start()
load_dotenv()

def create_embed(author, description, url = None, title = None):
    author_dict = {'name': author.display_name, 'icon_url': author.display_avatar.url}
    embed_dict = {'author': author_dict, 'description': description, 'color': 0x1abc9c}

    if url:
        embed_dict['url'] = url
    if title:
        embed_dict['title'] = title

    em = discord.Embed.from_dict(embed_dict)
    return em

class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(intents=intents, command_prefix='.')

    async def on_ready(self) -> None:
        print(f'Logged in {self.user} | {self.user.id}')

    async def setup_hook(self) -> None:
        handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        discord.utils.setup_logging(level=logging.INFO, handler=handler, root=False)

async def main():
    bot = Bot()
    bot.remove_command('help')
    bot.coin_responses = ['heads', 'tails']

    def is_owner():
        def predicate(ctx):
            return ctx.message.author.id == 819288373901918218
        return commands.check(predicate)

    # Owner commands
    @bot.command()
    @is_owner()
    async def leave_guild(ctx):
        await ctx.send('Goodbye.')
        await ctx.guild.leave()

    @bot.command()
    @is_owner()
    async def shutdown(ctx):
        try:
            await ctx.send('Shutting down...')
            await bot.close()
        except Exception as error:
            print(error)
            await ctx.send('Something went wrong.')

    # Info commands
    @bot.command()
    @commands.cooldown(1, 1)
    async def help(ctx):
        em = create_embed(ctx.author, "lol there is no help message yet")
        await ctx.send(embed=em)

    # Fun commands
    @bot.command(aliases=['pfp'])
    async def avatar(ctx, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(member.display_avatar)

    @bot.command()
    async def ping(ctx):
        em = create_embed(ctx.author, 'pong')
        await ctx.send(embed=em)

    async with bot:
        await bot.start(os.getenv("TOKEN"))

if __name__ == '__main__':
    asyncio.run(main())