-- Таблица ролей (права доступа к боту)
CREATE TABLE
    IF NOT EXISTS roles (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL -- Примеры: manager, employee, intern
    );

-- Таблица пользователей
CREATE TABLE
    IF NOT EXISTS users (
        tg_id BIGINT PRIMARY KEY, -- Telegram ID пользователя
        role_id INT NOT NULL REFERENCES roles (id), -- Связь с таблицей ролей по названию роли
        full_name TEXT,
        created_at TIMESTAMP DEFAULT NOW ()
    );

-- Таблица для хранения обучающих модулей
CREATE TABLE IF NOT EXISTS modules (
    id SERIAL PRIMARY KEY,                  -- Уникальный идентификатор модуля
    title TEXT NOT NULL,                    -- Название модуля
    description TEXT,                       -- Описание модуля
    created_at TIMESTAMP DEFAULT NOW()      -- Дата создания модуля
);

-- Таблица для хранения уроков в модулях
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,                  -- Уникальный идентификатор урока
    module_id INT REFERENCES modules(id) ON DELETE CASCADE,  -- Связь с модулем
    title TEXT NOT NULL,                    -- Название урока
    content TEXT,                           -- Текстовое содержание урока
    file_ids TEXT[],                        -- Список ID загруженных файлов (документы, изображения)
    video_ids TEXT[],                       -- Список ID видеоматериалов
    lesson_order INT NOT NULL,              -- Порядок урока в модуле
    created_at TIMESTAMP DEFAULT NOW()      -- Дата добавления урока
);

-- Таблица для хранения тестов после модулей
CREATE TABLE IF NOT EXISTS tests (
    id SERIAL PRIMARY KEY,                  -- Уникальный идентификатор теста
    module_id INT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,  -- Привязка к модулю
    question TEXT NOT NULL,                 -- Вопрос
    option_1 TEXT NOT NULL,                 -- Вариант 1
    option_2 TEXT NOT NULL,                 -- Вариант 2
    option_3 TEXT NOT NULL,                 -- Вариант 3
    option_4 TEXT NOT NULL,                 -- Вариант 4
    correct_option INT NOT NULL             -- Номер правильного варианта
);

-- Таблица для хранения результатов тестов после модулей
CREATE TABLE IF NOT EXISTS user_module_progress (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(tg_id) ON DELETE CASCADE,
    module_id INT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    is_completed BOOLEAN DEFAULT FALSE,
    can_access BOOLEAN DEFAULT FALSE,
    last_attempt TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, module_id) 
);

-- Таблица вопросов аттестации
CREATE TABLE IF NOT EXISTS final_exam_questions (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,                 -- Текст вопроса
    is_open_question BOOLEAN DEFAULT FALSE, -- Если TRUE, значит, нужен текстовый ответ
    option_1 TEXT,                          -- Вариант 1 (если is_open_question = FALSE)
    option_2 TEXT,
    option_3 TEXT,
    option_4 TEXT,
    correct_option INT                      -- Номер правильного ответа (если is_open_question = FALSE)
);

-- Таблица ответов пользователей
CREATE TABLE IF NOT EXISTS final_exam_answers (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(tg_id) ON DELETE CASCADE,
    question_id INT NOT NULL REFERENCES final_exam_questions(id) ON DELETE CASCADE,
    chosen_option INT,                        -- Выбранный вариант ответа (если вопрос с вариантами)
    open_answer TEXT,                         -- Развёрнутый ответ (если вопрос открытый)
    is_correct BOOLEAN                        -- TRUE, если ответ правильный
);

-- Таблица результатов аттестации
CREATE TABLE IF NOT EXISTS final_exam_results (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(tg_id) ON DELETE CASCADE,
    total_questions INT NOT NULL,             -- Количество вопросов
    correct_answers INT NOT NULL,             -- Количество правильных ответов
    passed BOOLEAN DEFAULT FALSE,             -- Итоговый результат (TRUE, если прошёл)
    exam_date TIMESTAMP DEFAULT NOW()         -- Дата прохождения
);


-- Наполнение таблицы ролей
INSERT INTO
    roles (name)
VALUES
    ('manager'),
    ('employee'),
    ('intern');

-- Наполнение таблицы пользователей
INSERT INTO
    users (tg_id, role_id, full_name)
VALUES
    (595410701, 1, 'Алексашин Артем Александрович');