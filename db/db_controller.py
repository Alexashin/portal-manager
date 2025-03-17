import asyncpg
import logging
from config_loader import DATABASE_URL

# Создание пула подключений к БД
db_pool: asyncpg.Pool = None

log = logging.getLogger(__name__)


# Инициализация пула подключений
async def init_db():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        log.debug("Пул БД создан.")


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
        try:
            role = await connection.fetchval(query, tg_id)
            return role if role else "unknown"
        except asyncpg.DataError as e:
            print(f"Ошибка типа данных в get_user_role: {e}")
            return "unknown"


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
    ORDER BY m.id ASC;
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


async def get_admin_id():
    query = "SELECT tg_id FROM users WHERE role_id = (SELECT id FROM roles WHERE name = 'manager') LIMIT 1"
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        admin = await connection.fetchrow(query)
        return admin["tg_id"] if admin else None


# Получаем первый модуль
async def get_first_module():
    query = """
    SELECT id, title, description
    FROM modules
    ORDER BY id ASC
    LIMIT 1
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetchrow(query)


# Получение следующего модуля
async def get_next_module_id(current_module_id: int):
    query = """
    SELECT id FROM modules
    WHERE id > $1
    ORDER BY id ASC
    LIMIT 1
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        row = await connection.fetchrow(query, current_module_id)
    return row["id"] if row else None


# Делаем модуль доступным для стажёра
async def make_module_accessible(user_id: int, module_id: int):
    query = """
    INSERT INTO user_module_progress (user_id, module_id, can_access)
    VALUES ($1, $2, TRUE)
    ON CONFLICT (user_id, module_id) DO UPDATE 
    SET can_access = EXCLUDED.can_access
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, user_id, module_id)


# Завершение аттестации
async def save_exam_result(
    user_id: int,
    total_questions: int,
    correct_answers: int,
    passed: bool,
    attempt_number: int,
):
    query = """
    INSERT INTO final_exam_results (user_id, attempt_number, total_questions, correct_answers, passed, attempt_date)
    VALUES ($1, $2, $3, $4, $5, NOW())
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(
            query, user_id, attempt_number, total_questions, correct_answers, passed
        )


# Сохранение ответов пользователя на финальную аттестацию
async def save_exam_answers(user_id: int, answers: list, attempt_number: int):
    query = """
    INSERT INTO final_exam_answers (user_id, attempt_number, question_id, chosen_option, open_answer, is_correct, timestamp)
    VALUES ($1, $2, $3, $4, $5, $6, NOW())
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        async with connection.transaction():
            for answer in answers:
                await connection.execute(
                    query,
                    user_id,
                    attempt_number,
                    answer["question_id"],
                    answer.get("chosen_option"),  # NULL для открытых вопросов
                    answer.get("open_answer"),  # NULL для тестовых вопросов
                    answer.get("is_correct"),  # NULL для открытых вопросов
                )


# Добавление вопроса в финальную аттестацию
async def add_final_exam_question(
    question: str,
    is_open_question: bool,
    options: list = None,
    correct_option: int = None,
):
    query = """
    INSERT INTO final_exam_questions (question, is_open_question, option_1, option_2, option_3, option_4, correct_option)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(
            query,
            question,
            is_open_question,
            options[0] if options else None,
            options[1] if options else None,
            options[2] if options else None,
            options[3] if options else None,
            correct_option,
        )


# Получение всех вопросов финальной аттестации
async def get_final_exam_questions():
    query = "SELECT * FROM final_exam_questions"
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetch(query)


# Удаление всех вопросов финальной аттестации
async def delete_all_final_exam_questions():
    query = "DELETE FROM final_exam_questions"
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query)


# Проверка доступа к финальной аттестации
async def check_final_exam_access(user_id: int) -> bool:
    query = """
    SELECT COUNT(*) = (SELECT COUNT(*) FROM modules) 
    FROM user_module_progress 
    WHERE user_id = $1 AND is_completed = TRUE;
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetchval(query, user_id)


async def get_user_exam_attempts(user_id: int):
    query = """
    SELECT attempt_number, attempt_date, correct_answers, total_questions, passed
    FROM final_exam_results
    WHERE user_id = $1
    ORDER BY attempt_number DESC
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetch(query, user_id)


async def get_exam_attempt_answers(user_id: int, attempt_number: int):
    query = """SELECT q.question, 
            a.chosen_option, 
            a.open_answer, 
            a.is_correct, 
            a.timestamp, 
            CASE a.chosen_option
                WHEN 1 THEN q.option_1
                WHEN 2 THEN q.option_2
                WHEN 3 THEN q.option_3
                WHEN 4 THEN q.option_4
                ELSE NULL
            END AS chosen_option_text
            FROM final_exam_answers a
            JOIN final_exam_questions q ON a.question_id = q.id
            WHERE a.user_id = $1 AND a.attempt_number = $2
            ORDER BY a.timestamp ASC
            """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetch(query, user_id, attempt_number)


async def get_next_attempt_number(user_id: int):
    query = """
    SELECT COALESCE(MAX(attempt_number), 0) + 1
    FROM final_exam_results
    WHERE user_id = $1
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetchval(query, user_id)


async def reject_last_exam_attempt(user_id: int):
    query = """
    UPDATE final_exam_results
    SET passed = FALSE
    WHERE user_id = $1
    AND attempt_number = (SELECT MAX(attempt_number) FROM final_exam_results WHERE user_id = $1)
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, user_id)


async def promote_to_employee(user_id: int):
    query = """
    UPDATE users SET role_id = (SELECT id FROM roles WHERE name = 'employee')
    WHERE tg_id = $1
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, user_id)


async def get_all_users():
    query = """
    SELECT u.tg_id, u.full_name, r.name AS role
    FROM users u
    JOIN roles r ON u.role_id = r.id
    ORDER BY r.name ASC, u.full_name ASC
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetch(query)


async def get_employee_info(user_id: int):
    query = """
    SELECT full_name, created_at FROM users WHERE tg_id = $1
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetchrow(query, user_id)


async def update_user_role(user_id: int, new_role: str):
    query = """
    UPDATE users SET role_id = (SELECT id FROM roles WHERE name = $1) WHERE tg_id = $2
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, new_role, user_id)


async def delete_employee(user_id: int):
    query = "DELETE FROM users WHERE tg_id = $1"
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, user_id)


async def add_employee(user_id: int, full_name: str, role: str):
    query = """
    INSERT INTO users (tg_id, role_id, full_name) 
    VALUES ($1, (SELECT id FROM roles WHERE name = $2), $3)
    ON CONFLICT (tg_id) DO UPDATE SET role_id = (SELECT id FROM roles WHERE name = $2), full_name = $3
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, user_id, role, full_name)


# Получение общей статистики по пользователям
async def get_user_statistics():
    query = """
    SELECT 
        (SELECT COUNT(*) FROM users WHERE role_id = (SELECT id FROM roles WHERE name = 'manager')) AS managers,
        (SELECT COUNT(*) FROM users WHERE role_id = (SELECT id FROM roles WHERE name = 'employee')) AS employees,
        (SELECT COUNT(*) FROM users WHERE role_id = (SELECT id FROM roles WHERE name = 'intern')) AS interns;
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetchrow(query)


# Получение статистики по обучению
async def get_training_statistics():
    query = """
    SELECT 
        (SELECT COUNT(*) FROM modules) AS total_modules,
        (SELECT COUNT(*) FROM lessons) AS total_lessons,
        (SELECT COUNT(*) FROM tests) AS total_tests,
        (SELECT COUNT(*) FROM final_exam_questions) AS total_exam_questions;
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetchrow(query)


# Получение статистики прогресса стажёров
async def get_progress_statistics():
    query = """
    SELECT 
        COUNT(*) AS completed_modules,
        AVG(correct_answers::float / total_questions) * 100 AS avg_test_score
    FROM final_exam_results
    WHERE passed = TRUE;
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetchrow(query)


# Получение ТОП-5 стажёров по количеству завершённых модулей
async def get_top_interns():
    query = """
    SELECT u.full_name, COUNT(ump.module_id) AS completed_modules
    FROM user_module_progress ump
    JOIN users u ON ump.user_id = u.tg_id
    WHERE ump.is_completed = TRUE
    GROUP BY u.full_name
    ORDER BY completed_modules DESC
    LIMIT 5;
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        return await connection.fetch(query)


# Получение значения настройки
async def get_bot_setting(setting_key: str):
    query = "SELECT value FROM bot_settings WHERE key = $1"
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        result = await connection.fetchval(query, setting_key)
    return result


# Обновление значения настройки
async def update_bot_setting(setting_key: str, new_value: str):
    query = """
    INSERT INTO bot_settings (key, value) VALUES ($1, $2)
    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
    """
    conn = await get_db_connection()
    async with conn.acquire() as connection:
        await connection.execute(query, setting_key, new_value)


async def get_lesson_by_id(lesson_id: int):
    """
    Получает информацию об уроке из БД.
    """
    query = """
    SELECT id, module_id, title, content, file_ids, video_ids, lesson_order, created_at
    FROM lessons
    WHERE id = $1
    """
    conn = await get_db_connection()
    try:
        async with conn.acquire() as connection:
            lesson = await connection.fetchrow(query, lesson_id)
            return dict(lesson) if lesson else None
    except Exception as e:
        log.error(f"Ошибка при получении урока {lesson_id}: {e}")
        return None
