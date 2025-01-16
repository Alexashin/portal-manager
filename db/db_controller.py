import asyncpg
from config_loader import DATABASE_URL

# Создание пула подключений к БД
db_pool: asyncpg.Pool = None

# Инициализация пула подключений
async def init_db():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(DATABASE_URL)

# Получение подключения из пула
async def get_db_connection():
    if db_pool is None:
        await init_db()
    return db_pool

# Создание нового модуля
async def create_module(title: str, description: str):
    query = """
    INSERT INTO modules (title, description)
    VALUES ($1, $2)
    RETURNING id
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        module_id = await connection.fetchval(query, title, description)
    return module_id

# Добавление урока к модулю (с поддержкой нескольких видео)
async def add_lesson(module_id: int, title: str, content: str, file_ids: list, video_ids: list, order: int):
    query = """
    INSERT INTO lessons (module_id, title, content, file_ids, video_ids, lesson_order)
    VALUES ($1, $2, $3, $4, $5, $6)
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, module_id, title, content, file_ids, video_ids, order)

# Получение всех модулей
async def get_all_modules():
    query = "SELECT * FROM modules"
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        modules = await connection.fetch(query)
    return modules

# Получение всех уроков по модулю
async def get_lessons_by_module(module_id: int):
    query = """
    SELECT * FROM lessons
    WHERE module_id = $1
    ORDER BY lesson_order
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        lessons = await connection.fetch(query, module_id)
    return lessons

# Удаление модуля по ID
async def delete_module(module_id: int):
    query = "DELETE FROM modules WHERE id = $1"
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, module_id)

# Получение роли пользователя по Telegram ID
async def get_user_role(tg_id: int) -> str:
    query = """
    SELECT r.name FROM users u
    JOIN roles r ON u.role_id = r.id
    WHERE u.tg_id = $1
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        role = await connection.fetchval(query, tg_id)
    return role

# Получение всех модулей
async def get_all_modules():
    query = """
    SELECT id, title, description
    FROM modules
    ORDER BY id
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        modules = await connection.fetch(query)
    return [dict(module) for module in modules]