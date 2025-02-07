DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS favorite_items;


CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    country VARCHAR(255) NOT NULL,
    city VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_logged BOOLEAN DEFAULT TRUE NOT NULL
);

CREATE TABLE item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    item_stock INT NOT NULL
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATE NOT NULL,
    shipping_address TEXT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status ENUM('TEMP', 'CLOSE') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES item(id)
);

CREATE TABLE favorite_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (item_id) REFERENCES item(id)
);

INSERT INTO item (name, price, item_stock)
VALUES
    ('Bluetooth Speaker', 49.99, 50),
    ('Portable Mini Speaker', 29.99, 30),
    ('Home Theater Speaker', 200.50, 15),
    ('Waterproof Bluetooth Speaker', 65.70, 25),
    ('Smart Speaker with Voice Assistant', 129.99, 20),
    ('Soundbar with Subwoofer', 249.99, 10),
    ('Outdoor Wireless Speaker', 89.99, 18),
    ('Bookshelf Speakers', 149.99, 12),
    ('Car Audio Speaker System', 119.99, 8),
    ('Party Speaker with LED Lights', 179.99, 10),
    ('Ceiling Mount Speakers', 99.99, 30),
    ('Speaker Stands (Pair)', 39.99, 40),
    ('High-Fidelity Studio Monitor Speaker', 210.30, 10),
    ('Speaker Wall Mount Brackets', 24.99, 60),
    ('Wireless Speaker Charging Dock', 34.99, 35),
    ('WiFi Multi-Room Speaker', 160.50, 15),
    ('Gaming Speaker System', 89.99, 20),
    ('Compact Desktop Speaker', 44.99, 25),
    ('Wireless Earbuds with Speaker', 84.90, 50),
    ('Vintage Style Wooden Speaker', 99.99, 10),
    ('Eco Speaker System', 29.99, 0),
    ('Camping Speaker', 41.50, 2);

INSERT INTO users (first_name, last_name, email, phone, address, country, city, username, hashed_password, is_logged)
VALUES
    ('Liam', 'Smith', 'liam.smith@example.com', '555-123-4567', '123 Main St', 'USA', 'New York', 'lsmith', '$2y$10$hashed_password_1', TRUE),
    ('Olivia', 'Johnson', 'olivia.johnson@example.com', '555-987-6543', '456 Elm Ave', 'Canada', 'Toronto', 'ojohnson', '$2y$10$hashed_password_2', TRUE),
    ('Noah', 'Williams', 'noah.williams@example.com', '555-555-5555', '789 Oak Ln', 'UK', 'London', 'nwilliams', '$2y$10$hashed_password_3', TRUE),
    ('Emma', 'Brown', 'emma.brown@example.com', '555-111-2222', '101 Pine St', 'Australia', 'Sydney', 'ebrown', '$2y$10$hashed_password_4', TRUE),
    ('William', 'Davis', 'william.davis@example.com', '555-333-4444', '222 Maple Dr', 'Germany', 'Berlin', 'wdavis', '$2y$10$hashed_password_5', TRUE),
    ('Ava', 'Garcia', 'ava.garcia@example.com', '555-666-7777', '333 Cedar Rd', 'Spain', 'Madrid', 'agarcia', '$2y$10$hashed_password_6', TRUE),
    ('James', 'Rodriguez', 'james.rodriguez@example.com', '555-888-9999', '444 Birch Ct', 'Mexico', 'Mexico City', 'jrodriguez', '$2y$10$hashed_password_7', TRUE),
    ('Isabella', 'Wilson', 'isabella.wilson@example.com', '555-000-1111', '555 Willow Pl', 'France', 'Paris', 'iwilson', '$2y$10$hashed_password_8', TRUE),
    ('Ethan', 'Martinez', 'ethan.martinez@example.com', '555-222-3333', '666 Redwood Way', 'Brazil', 'Rio de Janeiro', 'emartinez', '$2y$10$hashed_password_9', TRUE),
    ('Mia', 'Anderson', 'mia.anderson@example.com', '555-444-5555', '777 Oak Ave', 'Japan', 'Tokyo', 'manderson', '$2y$10$hashed_password_10', TRUE);
