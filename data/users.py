from pathlib import Path
import aiosqlite


async def get_user(user_id: int):
    async with aiosqlite.connect(Path('data', 'db.db')) as db:
        async with db.execute('SELECT * FROM users WHERE id = ?', (user_id,)) as cursor:
            user = await cursor.fetchone()
            return user


async def user_is_in_table(user_id: int) -> bool:
    user = await get_user(user_id)
    if user:
        return True


async def get_list_admin() -> list:
    result = None
    async with aiosqlite.connect(Path('data', 'db.db')) as db:
        async with db.execute('SELECT * FROM users WHERE is_admin = 1') as cursor:
            rows = await cursor.fetchall()
            result = [row[0] for row in rows]
    return result


async def add_user_to_data_base(user_id, username, is_admin=False, name='Аноним'):
    async with aiosqlite.connect(Path('data', 'db.db')) as db:
        is_table = await user_is_in_table(user_id=user_id)
        if not is_table:
            await db.execute('INSERT INTO users (id, username, is_admin, name) VALUES (?,?,?,?)',
                             (user_id, username, is_admin, name))

        else:
            await db.execute('''
            UPDATE users 
            SET username = ?,
                name = ?
            WHERE id = ?''', (username, name, user_id))
        await db.commit()


if __name__ == '__main__':
    pass
