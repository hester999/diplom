-- Шаг 1: Создание базы данных
CREATE DATABASE vulnerable_db;

-- Подключаемся к только что созданной базе данных
\c vulnerable_db;

-- Шаг 2: Создание таблиц

-- Таблица пользователей
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Таблица заказов
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_name VARCHAR(100),
    order_date TIMESTAMP
);

-- Таблица продуктов
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2)
);

-- Таблица конфиденциальных данных
CREATE TABLE secret_data (
    id SERIAL PRIMARY KEY,
    secret_info TEXT,
    user_id INT REFERENCES users(id)
);

-- Шаг 3: Вставка тестовых данных

-- Вставка пользователей
INSERT INTO users (username, password) VALUES
('admin', 'admin123'),
('user1', 'password1'),
('user2', 'password2');

-- Вставка заказов
INSERT INTO orders (user_id, product_name, order_date) VALUES
(1, 'Product A', '2023-01-01'),
(2, 'Product B', '2023-01-02'),
(3, 'Product C', '2023-01-03');

-- Вставка продуктов
INSERT INTO products (name, price) VALUES
('Product A', 10.99),
('Product B', 20.49),
('Product C', 30.79);

-- Вставка конфиденциальных данных
INSERT INTO secret_data (secret_info, user_id) VALUES
('Super secret info for admin', 1),
('Sensitive data for user1', 2),
('Confidential data for user2', 3)


CREATE TABLE stolen_cookies (
    id SERIAL PRIMARY KEY,
    cookie TEXT NOT NULL,
    stolen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
