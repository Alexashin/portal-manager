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
async def add_lesson(
    module_id: int,
    title: str,
    content: str,
    file_ids: list,
    video_ids: list,
    order: int,
):
    query = """
    INSERT INTO lessons (module_id, title, content, file_ids, video_ids, lesson_order)
    VALUES ($1, $2, $3, $4, $5, $6)
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(
            query, module_id, title, content, file_ids, video_ids, order
        )


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


# Обновить модуль (название и описание)
async def update_module(module_id: int, new_title: str, new_description: str):
    if new_title != "":
        if new_description != "":
            query = "UPDATE modules SET title = $1, description = $2 WHERE id = $3"
            conn = await get_db_connection()
            async with conn.acquire() as connection:
                await connection.execute(query, new_title, new_description, module_id)
            return
        else:
            query = "UPDATE modules SET title = $1 WHERE id = $2"
            conn = await get_db_connection()
            async with conn.acquire() as connection:
                await connection.execute(query, new_title, module_id)
            return
    if new_description != "":
        query = "UPDATE modules SET description = $1 WHERE id = $2"
        conn = await get_db_connection()
        async with conn.acquire() as connection:
            await connection.execute(query, new_description, module_id)


# Удалить модуль
async def delete_module(module_id: int):
    query = "DELETE FROM modules WHERE id = $1"
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, module_id)


# Удалить конкретный урок по ID
async def delete_lesson(lesson_id: int):
    query = "DELETE FROM lessons WHERE id = $1"
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, lesson_id)


# Обновить урок (название, содержание, файлы, видео)
async def update_lesson(
    lesson_id: int,
    new_title: str,
    new_content: str,
    new_file_ids: list,
    new_video_ids: list,
):
    query = """
    UPDATE lessons
    SET title = $1, content = $2, file_ids = $3, video_ids = $4
    WHERE id = $5
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(
            query, new_title, new_content, new_file_ids, new_video_ids, lesson_id
        )


# Добавление нового урока в модуль
async def add_new_lesson_to_module(
    module_id: int, title: str, content: str, file_ids: list, video_ids: list
):
    query = """
    INSERT INTO lessons (module_id, title, content, file_ids, video_ids, lesson_order)
    VALUES ($1, $2, $3, $4, $5, (SELECT COALESCE(MAX(lesson_order), 0) + 1 FROM lessons WHERE module_id = $1))
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, module_id, title, content, file_ids, video_ids)


# Добавление вопроса в тест
async def add_question_to_test(
    module_id: int, question: str, options: list, correct_option: int
):
    query = """
    INSERT INTO tests (module_id, question, option_1, option_2, option_3, option_4, correct_option)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(
            query,
            module_id,
            question,
            options[0],
            options[1],
            options[2],
            options[3],
            correct_option,
        )


# Получение вопросов теста
async def get_test_questions(module_id: int):
    query = """
    SELECT id, question, option_1, option_2, option_3, option_4, correct_option
    FROM tests
    WHERE module_id = $1
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetch(query, module_id)


# Удаление теста для модуля
async def delete_test(module_id: int):
    query = "DELETE FROM tests WHERE module_id = $1"
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, module_id)


# Получение доступных модулей
async def get_available_modules_for_user(user_id: int):
    query = """
    SELECT m.id, m.title, m.description
    FROM modules m
    JOIN user_module_progress ump ON m.id = ump.module_id
    WHERE ump.user_id = $1 AND ump.can_access = TRUE
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetch(query, user_id)


# Получение прогресса пользователя
async def get_user_progress(user_id: int):
    query = """
    SELECT m.title, ump.last_attempt AS completed_at
    FROM user_module_progress ump
    JOIN modules m ON ump.module_id = m.id
    WHERE ump.user_id = $1 AND ump.is_completed = TRUE
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetch(query, user_id)

# Обновление прогресса стажера
async def update_module_progress(user_id: int, module_id: int, is_completed: bool):
    query = """
    UPDATE user_module_progress
    SET is_completed = $1, last_attempt = NOW()
    WHERE user_id = $2 AND module_id = $3
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, is_completed, user_id, module_id)

