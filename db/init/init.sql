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