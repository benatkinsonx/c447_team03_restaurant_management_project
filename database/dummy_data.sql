USE testproject;

-- =========================
-- ROLES
-- =========================

INSERT INTO Roles (role_name)
VALUES
('Customer'),
('Admin'),
('Owner');

-- =========================
-- ADDRESSES
-- =========================

INSERT INTO Address
(addr1, addr2, city, post_code)
VALUES
('12 High Street', NULL, 'London', 'SW1A1AA'),
('45 Market Road', 'Flat 2', 'Manchester', 'M11AA'),
('78 King Street', NULL, 'Leeds', 'LS12AB'),
('3 Victoria Avenue', NULL, 'Bristol', 'BS11AA');

-- =========================
-- USERS
-- NOTE: Replace password_hash
-- with real bcrypt hashes if needed
-- =========================

INSERT INTO Users
(role_id, addr_id, first_name, last_name, email, password_hash, phone_num, reward_points)
VALUES
(3, 1, 'Restaurant', 'Owner', 'owner@test.com', 'password', '07111111111', 0),
(2, 2, 'Alice', 'Admin', 'admin@test.com', 'password', '07222222222', 0),
(1, 3, 'Ben', 'Atkinson', 'ben@test.com', 'password', '07333333333', 250),
(1, 4, 'Sarah', 'Jones', 'sarah@test.com', 'password', '07444444444', 120);

-- =========================
-- CATEGORIES
-- =========================

INSERT INTO Category
(category, category_desc)
VALUES
('Food', 'Food and drink items'),
('Merchandise', 'Restaurant merchandise');

-- =========================
-- MENU ITEMS
-- =========================

INSERT INTO MenuItems
(cat_id, item_name, is_veg, price, is_available)
VALUES
(1, 'Margherita Pizza', TRUE, 11.99, TRUE),
(1, 'Pepperoni Pizza', FALSE, 13.99, TRUE),
(1, 'Garlic Bread', TRUE, 4.99, TRUE),
(1, 'Chicken Burger', FALSE, 12.50, TRUE),
(1, 'Chocolate Brownie', TRUE, 5.50, TRUE),
(1, 'Coca Cola', TRUE, 2.50, TRUE),

(2, 'Restaurant Mug', TRUE, 8.99, TRUE),
(2, 'Branded T-Shirt', TRUE, 19.99, TRUE),
(2, 'Baseball Cap', TRUE, 14.99, TRUE);

-- =========================
-- RESTAURANT TABLES
-- =========================

INSERT INTO RestaurantTables
(table_num, capacity, table_status)
VALUES
(1, 2, 'available'),
(2, 2, 'available'),
(3, 4, 'available'),
(4, 4, 'available'),
(5, 6, 'available'),
(6, 8, 'available');

-- =========================
-- REWARDS
-- =========================

INSERT INTO Rewards
(reward_name, reward_desc, points, cost_multiplier, active)
VALUES
('5OFF', '5 percent off next order', 100, 0.95, TRUE),
('10OFF', '10 percent off next order', 200, 0.90, TRUE),
('15OFF', '15 percent off next order', 300, 0.85, TRUE);

-- =========================
-- ORDERS
-- =========================

INSERT INTO Orders
(user_id, order_status, total_price)
VALUES
(3, 'completed', 28.48),
(4, 'completed', 15.00),
(3, 'placed', 11.99);

-- =========================
-- ORDER ITEMS
-- =========================

INSERT INTO OrderItems
(order_id, menu_id, quantity, item_price)
VALUES
(1, 1, 2, 11.99),
(1, 3, 1, 4.99),

(2, 4, 1, 12.50),
(2, 6, 1, 2.50),

(3, 1, 1, 11.99);

-- =========================
-- PAYMENTS
-- =========================

INSERT INTO Payments
(order_id, user_id, amount, payment_status)
VALUES
(1, 3, 28.48, 'completed'),
(2, 4, 15.00, 'completed');

-- =========================
-- RESERVATIONS
-- =========================

INSERT INTO Reservations
(user_id, table_id, booking_date, booking_time, size, status)
VALUES
(3, 3, '2026-06-20', '19:00:00', 4, 'booked'),
(4, 1, '2026-06-21', '18:30:00', 2, 'booked');

-- =========================
-- REDEEMED REWARDS
-- =========================

INSERT INTO Redeemed
(user_id, reward_id, order_id)
VALUES
(3, 1, 1);

-- =========================
-- OPTIONAL VERIFICATION
-- =========================

SELECT * FROM Roles;
SELECT * FROM Users;
SELECT * FROM Category;
SELECT * FROM MenuItems;
SELECT * FROM Orders;
SELECT * FROM OrderItems;
SELECT * FROM Payments;
SELECT * FROM Reservations;
SELECT * FROM Rewards;
SELECT * FROM Redeemed;