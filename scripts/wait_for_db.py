import asyncio
import os

import asyncpg

DB_URL = os.environ.get("DATABASE_URL", "").replace("postgresql+asyncpg", "postgresql")


async def wait_for_db():
    while True:
        try:
            conn = await asyncpg.connect(DB_URL)
            await conn.close()
            print("Database is ready!", flush=True)
            break
        except Exception as exc:
            print("Waiting for database...", exc, flush=True)
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(wait_for_db())
