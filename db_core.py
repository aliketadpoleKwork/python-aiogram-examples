import asyncpg
import logging

# Пример модуля для работы с PostgreSQL через пул соединений
class DatabaseManager:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create_tables(self):
        """Инициализация структуры БД"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    phone TEXT UNIQUE,
                    reg_date TIMESTAMP,
                    sub_end_date TIMESTAMP,
                    max_tasks INTEGER
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS requests_queue (
                    id SERIAL PRIMARY KEY,
                    chat_id TEXT,
                    text TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
        logging.info("База данных успешно инициализирована.")

    async def get_user_profile(self, user_id: str) -> dict | None:
        """Получение данных пользователя"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT reg_date, sub_end_date, max_tasks FROM users WHERE user_id = $1", 
                user_id
            )
            return dict(row) if row else None

    async def update_subscription(self, user_id: str, new_end_date, max_tasks: int):
        """Обновление лимитов и сроков"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET sub_end_date = $1, max_tasks = $2 WHERE user_id = $3",
                new_end_date, max_tasks, user_id
            )
