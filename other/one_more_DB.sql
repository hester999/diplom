
-- Шаг 2: Создание таблиц, если они еще не существуют

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Таблица заказов
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_name VARCHAR(100),
    order_date TIMESTAMP
);

-- Таблица продуктов
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2)
);

-- Таблица конфиденциальных данных
CREATE TABLE IF NOT EXISTS secret_data (
    id SERIAL PRIMARY KEY,
    secret_info TEXT,
    user_id INT REFERENCES users(id)
);

-- Шаг 3: Вставка тестовых данных

-- Вставка пользователей (включая main_admin), если они еще не существуют
INSERT INTO users (username, password)
SELECT 'admin', 'admin123'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

INSERT INTO users (username, password)
SELECT 'user1', 'password1'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'user1');

INSERT INTO users (username, password)
SELECT 'user2', 'password2'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'user2');

INSERT INTO users (username, password)
SELECT 'main_admin', 'mainadminpassword'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'main_admin');  -- Добавляем main_admin с произвольным паролем

-- Генерация дополнительных пользователей (до 200)
DO $$
DECLARE
    i INT := 3;
BEGIN
    FOR i IN 3..200 LOOP
        -- Добавляем пользователей, если они еще не существуют
        EXECUTE 'INSERT INTO users (username, password) SELECT ''user'' || $1, ''password'' || $1 WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = ''user'' || $1)' USING i;
    END LOOP;
END $$;

-- Вставка продуктов (100 продуктов), если они еще не существуют
DO $$
DECLARE
    i INT := 1;
BEGIN
    FOR i IN 1..100 LOOP
        -- Добавляем продукты, если они еще не существуют
        EXECUTE 'INSERT INTO products (name, price) SELECT ''Product '' || $1, ROUND(CAST(RANDOM() * (200 - 10) + 10 AS DECIMAL), 2) WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = ''Product '' || $1)' USING i;
    END LOOP;
END $$;

-- Вставка заказов для пользователей (по 100 заказов на каждого)
DO $$
DECLARE
    i INT := 1;
    j INT;
BEGIN
    FOR i IN 1..200 LOOP
        FOR j IN 1..100 LOOP
            -- Добавляем заказ, если он еще не существует
            EXECUTE 'INSERT INTO orders (user_id, product_name, order_date) SELECT $1, ''Product '' || ($2 % 100 + 1), NOW() WHERE NOT EXISTS (SELECT 1 FROM orders WHERE user_id = $1 AND product_name = ''Product '' || ($2 % 100 + 1))' USING i, j;
        END LOOP;
    END LOOP;
END $$;

-- Вставка конфиденциальных данных для каждого пользователя
DO $$
DECLARE
    i INT := 1;
BEGIN
    FOR i IN 1..200 LOOP
        -- Добавляем конфиденциальные данные, если они еще не существуют
        EXECUTE 'INSERT INTO secret_data (secret_info, user_id) SELECT ''Confidential data for user'' || $1, $1 WHERE NOT EXISTS (SELECT 1 FROM secret_data WHERE user_id = $1)' USING i;
    END LOOP;
END $$;
