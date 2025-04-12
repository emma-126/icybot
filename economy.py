import asyncio

class Economy:
    def __init__(self, bot):
        self.bot = bot

    async def check_balance(self, user_id):
        user_exists = await self.bot.database.query_user_exists(user_id)
        if user_exists is True:
            balance = await self._retrieve_balance(user_id)
            return balance
        else:
            values = (user_id, 100, 0)
            await self.bot.database.insert_money_data(values)
            balance = [100, 0, 100]
            return balance

    async def _retrieve_balance(self, user_id):
        row = await self.bot.database.query_money_data(user_id)
        wallet = row[1]
        vault = row[2]
        net_worth = wallet + vault
        balance = [wallet, vault, net_worth]
        return balance

    async def wallet_to_vault(self, user_id, amount):
        balance = await self.check_balance(user_id)
        if balance[0] < amount:
            return balance
        else:
            wallet = balance[0] - amount
            vault = balance[1] + amount
            values = (wallet, vault, user_id)
            await self.bot.database.update_money_data(values)
            return True

    async def vault_to_wallet(self, user_id, amount):
        balance = await self.check_balance(user_id)
        if balance[1] < amount:
            return balance
        else:
            wallet = balance[0] + amount
            vault = balance[1] - amount
            values = (wallet, vault, user_id)
            await self.bot.database.update_money_data(values)
            return True