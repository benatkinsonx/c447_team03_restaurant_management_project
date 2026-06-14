drop database testproject;

CREATE DATABASE testproject;

use testproject;

-- ROLES

CREATE TABLE Roles (
  role_id INT PRIMARY KEY AUTO_INCREMENT,
  role_name VARCHAR(50) NOT NULL UNIQUE
);

-- ADDRESS

CREATE TABLE Address (
  addr_id INT PRIMARY KEY AUTO_INCREMENT,
  addr1 VARCHAR(50),
  addr2 VARCHAR(50),
  city VARCHAR(50),
  post_code VARCHAR(10)
);

-- USERS

CREATE TABLE Users (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  role_id INT NOT NULL,
  addr_id INT,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  email VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  phone_num VARCHAR(20),
  reward_points INT NOT NULL DEFAULT 0,

  CONSTRAINT fk_users_role
    FOREIGN KEY (role_id) REFERENCES Roles(role_id),

  CONSTRAINT fk_users_address
    FOREIGN KEY (addr_id) REFERENCES Address(addr_id)
);

ALTER TABLE Users
MODIFY role_id INT NOT NULL DEFAULT 1;

-- CATEGORY

CREATE TABLE Category (
  cat_id INT PRIMARY KEY AUTO_INCREMENT,
  category VARCHAR(50) NOT NULL,
  category_desc VARCHAR(255)
);

ALTER TABLE Category
ADD CONSTRAINT category_name 
CHECK (category IN ('Food', 'Merchandise')
);

-- MENU ITEMS

CREATE TABLE MenuItems (
  menu_id INT PRIMARY KEY AUTO_INCREMENT,
  cat_id INT NOT NULL,
  item_name VARCHAR(50) NOT NULL,
  is_veg BOOLEAN,
  price DECIMAL(10,2) NOT NULL,
  is_available BOOLEAN NOT NULL DEFAULT TRUE,

  CONSTRAINT fk_menu_category
    FOREIGN KEY (cat_id) REFERENCES Category(cat_id)
);

-- ORDERS

CREATE TABLE Orders (
  order_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  order_status VARCHAR(30) NOT NULL DEFAULT 'placed',
  total_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,

  CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- ORDER ITEMS

CREATE TABLE OrderItems (
  order_item_id INT PRIMARY KEY AUTO_INCREMENT,
  order_id INT NOT NULL,
  menu_id INT NOT NULL,
  quantity INT NOT NULL,
  item_price DECIMAL(10,2) NOT NULL,

  CONSTRAINT fk_orderitems_order
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),

  CONSTRAINT fk_orderitems_menu
    FOREIGN KEY (menu_id) REFERENCES MenuItems(menu_id)
);

-- PAYMENTS

CREATE TABLE Payments (
  payment_id INT PRIMARY KEY AUTO_INCREMENT,
  order_id INT NOT NULL,
  user_id INT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  payment_status VARCHAR(30) NOT NULL DEFAULT 'pending',
  payment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_payments_order
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
  CONSTRAINT fk_user_id
	  FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- RESTAURANT TABLES

CREATE TABLE RestaurantTables (
  table_id INT PRIMARY KEY AUTO_INCREMENT,
  table_num INT NOT NULL UNIQUE,
  capacity INT NOT NULL,
  table_status VARCHAR(50) NOT NULL DEFAULT 'available'
);

-- RESERVATIONS

CREATE TABLE Reservations (
  reservation_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  table_id INT,
  booking_date DATE NOT NULL,
  booking_time TIME NOT NULL,
  size INT NOT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'booked',

  CONSTRAINT fk_reservations_user
    FOREIGN KEY (user_id) REFERENCES Users(user_id),

  CONSTRAINT fk_reservations_table
    FOREIGN KEY (table_id) REFERENCES RestaurantTables(table_id)
);


-- REWARDS

CREATE TABLE Rewards (
  reward_id INT PRIMARY KEY AUTO_INCREMENT,
  reward_name VARCHAR(50) NOT NULL,
  reward_desc VARCHAR(255),
  cost_multiplier float NOT NULL,
  points INT NOT NULL,
  active BOOLEAN NOT NULL DEFAULT TRUE
);

-- REDEEMED REWARDS
CREATE TABLE Redeemed (
  redeem_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  reward_id INT NOT NULL,
  order_id INT,
  redeem_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_redeemed_user
    FOREIGN KEY (user_id) REFERENCES Users(user_id),

  CONSTRAINT fk_redeemed_reward
    FOREIGN KEY (reward_id) REFERENCES Rewards(reward_id),

  CONSTRAINT fk_redeemed_order
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);