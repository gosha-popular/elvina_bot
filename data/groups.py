from pathlib import Path

import aiosqlite


async def get_list_group_mailing() -> list:
    result = None
    async with aiosqlite.connect(Path('data', 'db.db')) as db:
        async with db.execute('SELECT * FROM groups WHERE is_mailing = 1') as cursor:
            rows = await cursor.fetchall()
            result = [row[0] for row in rows]
    return result



async def add_group(group_id, title, is_mailing = False):
    async with aiosqlite.connect(Path('data', 'db.db')) as db:
        async with db.execute('SELECT * FROM groups WHERE id = ?', (group_id,)) as cursor:
            rows = await cursor.fetchall()
            if len(rows) == 0:
                await db.execute('INSERT INTO groups (id, title, is_mailing) VALUES (?,?,?)',
                                 (group_id, title, is_mailing))
            else:
                await db.execute('UPDATE groups SET id = ?, title = ?, is_mailing = ?', (group_id, title, is_mailing))
        await db.commit()
