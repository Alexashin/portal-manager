-- Таблица ролей (права доступа к боту)
CREATE TABLE
    IF NOT EXISTS roles (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL -- Примеры: manager, employee, intern
    );

-- Таблица пользователей
CREATE TABLE
    IF NOT EXISTS users (
        tg_id INT PRIMARY KEY, -- Telegram ID пользователя
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
    user_id INT NOT NULL REFERENCES users(tg_id) ON DELETE CASCADE,
    module_id INT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    is_completed BOOLEAN DEFAULT FALSE,     -- Завершил модуль
    can_access BOOLEAN DEFAULT FALSE,       -- Имеет доступ
    last_attempt TIMESTAMP DEFAULT NOW()    -- Дата последнего теста
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