import traceback
import logging

import asyncio
import random
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

from database import Database
from economy import Economy

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

        Bot.owner_user_id = int(os.getenv("OWNERUSERID"))

async def main():
    bot = Bot()
    bot.database = Database()
    bot.economy = Economy(bot)

    bot.remove_command('help')
    bot.coin_responses = ['heads', 'tails']

    def is_owner():
        def predicate(ctx):
            return ctx.message.author.id == bot.owner_user_id
        return commands.check(predicate)

    # Owner commands
    @bot.command()
    @is_owner()
    async def leave_guild(ctx):
        await ctx.send('Goodbye.')
        await ctx.guild.leave()

    @leave_guild.error
    async def on_leave_guild_error(ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"I'm sorry {ctx.author.display_name}, I'm afraid I can't do that.")
            return
        else:
            traceback.print_exc()

    @bot.command()
    @is_owner()
    async def shutdown(ctx):
        await ctx.send('Shutting down...')
        await bot.close()

    @shutdown.error
    async def on_shutdown_error(ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"I'm sorry {ctx.author.display_name}, I'm afraid I can't do that.")
            return
        else:
            traceback.print_exc()

    @bot.command()
    @is_owner()
    async def test(ctx):
        await ctx.send('test')

    @test.error
    async def on_test_error(ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"I'm sorry {ctx.author.display_name}, I'm afraid I can't do that.")
            return
        else:
            traceback.print_exc()

    # Info commands
    @bot.command()
    @commands.cooldown(1, 1)
    async def help(ctx):
        em = create_embed(ctx.author, "Commands: help, avatar, coinflip, ping, balance, deposit, withdraw")
        await ctx.send(embed=em)

    # Fun commands
    @bot.command(aliases=['pfp'])
    async def avatar(ctx, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send(member.display_avatar)

    @bot.command(aliases=['cf'])
    async def coinflip(ctx):
        em = create_embed(ctx.author, f'Flipping a coin... {random.choice(bot.coin_responses)}!')
        await ctx.send(embed=em)

    @bot.command()
    async def ping(ctx):
        em = create_embed(ctx.author, 'pong')
        await ctx.send(embed=em)

    # Economy commands
    @bot.command(aliases=['bal'])
    async def balance(ctx, member: discord.Member = None):
        member = member or ctx.author
        balance = await bot.economy.check_balance(member.id)
        em = create_embed(member, f'Wallet: {balance[0]}\nVault: {balance[1]}\nNet Worth: {balance[2]}')
        await ctx.send(embed=em)

    @bot.command(aliases=['dep'])
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def deposit(ctx, amount):
        amount = int(amount)
        if amount < 1:
            raise ValueError
        balance = await bot.economy.wallet_to_vault(ctx.author.id, amount)
        if balance is True:
            em = create_embed(ctx.author, f'Successfully deposited {amount} into your vault.')
        else:
            em = create_embed(ctx.author, f"You can't deposit {amount} into your vault, because you only have {balance[0]} in your wallet.")
        await ctx.send(embed=em)

    @deposit.error
    async def on_deposit_error(ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.ValueError):
            em = create_embed(ctx.author, "Please deposit an amount larger than zero.")
            await ctx.send(embed=em)
            return
        elif isinstance(error, commands.TypeError):
            em = create_embed(ctx.author, "Please enter your amount in numeric format.")
            await ctx.send(embed=em)
            return
        else:
            traceback.print_exc()

    @bot.command(aliases=['with'])
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def withdraw(ctx, amount):
        amount = int(amount)
        if amount < 1:
            raise ValueError
        balance = await bot.economy.vault_to_wallet(ctx.author.id, amount)
        if balance is True:
            em = create_embed(ctx.author, f'Successfully withdrew {amount} from your vault.')
        else:
            em = create_embed(ctx.author, f"You can't withdraw {amount} into your wallet, because you only have {balance[1]} in your vault.")
        await ctx.send(embed=em)

    @withdraw.error
    async def on_withdraw_error(ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.ValueError):
            em = create_embed(ctx.author, "Please withdraw an amount larger than zero.")
            await ctx.send(embed=em)
            return
        elif isinstance(error, commands.TypeError):
            em = create_embed(ctx.author, "Please enter your amount in numeric format.")
            await ctx.send(embed=em)
            return
        else:
            traceback.print_exc()

    async with bot:
        await bot.start(os.getenv("TOKEN"))

if __name__ == '__main__':
    asyncio.run(main())