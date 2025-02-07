from pathlib import Path

import aiosqlite


async def create_database():

    async with aiosqlite.connect(Path('data', 'db.db')) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        is_admin BOOLEAN DEFAULT FALSE,
        name TEXT
        )''')

        await db.execute('''CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY,
        title TEXT,
        is_mailing BOOLEAN DEFAULT FALSE
        )''')

        await db.commit()

