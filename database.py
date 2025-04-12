import asyncio
import asqlite

class Database:
    def __init__(self):
        self.money_db = 'databases/money.db'

    def _connect(self, db_file):
        return asqlite.connect(db_file)

    async def query_user_exists(self, user_id):
        async with self._connect(self.money_db) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT * FROM money WHERE id=?', (user_id,))
                row = await cursor.fetchone()
                if row is None:
                    return False
                else:
                    return True

    async def insert_money_data(self, values):
        async with self._connect(self.money_db) as conn:
            async with conn.cursor() as cursor:
                data = '''INSERT INTO money(id,wallet,vault)
                            VALUES(?,?,?)'''
                await cursor.execute(data, values)
                await conn.commit()
                return True

    async def update_money_data(self, values):
        async with self._connect(self.money_db) as conn:
            async with conn.cursor() as cursor:
                data = '''UPDATE money
                            SET wallet = ?,
                                vault = ?
                            WHERE id = ?'''
                await cursor.execute(data, values)
                await conn.commit()
                return True

    async def query_money_data(self, user_id):
        async with self._connect(self.money_db) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT * FROM money WHERE id=?', (user_id,))
                row = await cursor.fetchone()
                return row