-- Multi-Restaurant Menu Platform: Database Schema
-- Lavina House Brand Platform
-- MySQL 5.7+ compatible

CREATE DATABASE IF NOT EXISTS menu_platform
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE menu_platform;

-- Brand settings (single row)
CREATE TABLE brand_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL DEFAULT 'Lavina House',
    primary_color VARCHAR(7) DEFAULT '#C9A366',
    logo VARCHAR(255) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO brand_settings (brand_name, primary_color) VALUES ('Lavina House', '#C9A366');

-- Restaurants
CREATE TABLE restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(50) NOT NULL UNIQUE,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    logo VARCHAR(255) DEFAULT NULL,
    address_ar TEXT DEFAULT NULL,
    address_en TEXT DEFAULT NULL,
    phone VARCHAR(30) DEFAULT NULL,
    is_active TINYINT(1) DEFAULT 1,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Categories
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    image VARCHAR(255) DEFAULT NULL,
    is_featured TINYINT(1) DEFAULT 0,
    featured_type ENUM('most_ordered', 'fastest_ordered') DEFAULT NULL,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_restaurant (restaurant_id),
    INDEX idx_sort (restaurant_id, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Subcategories
CREATE TABLE subcategories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    INDEX idx_category (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Items
CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    subcategory_id INT DEFAULT NULL,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    price DECIMAL(10,3) NOT NULL DEFAULT 0,
    desc_ar TEXT DEFAULT NULL,
    desc_en TEXT DEFAULT NULL,
    image VARCHAR(255) DEFAULT NULL,
    spicy TINYINT(1) DEFAULT 0,
    recommended TINYINT(1) DEFAULT 0,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) ON DELETE SET NULL,
    INDEX idx_category (category_id),
    INDEX idx_subcategory (subcategory_id),
    INDEX idx_sort (category_id, subcategory_id, sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Variants
CREATE TABLE variants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    name_ar VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    price DECIMAL(10,3) DEFAULT NULL,
    desc_ar TEXT DEFAULT NULL,
    desc_en TEXT DEFAULT NULL,
    image VARCHAR(255) DEFAULT NULL,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    INDEX idx_item (item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Admins
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('super_admin', 'restaurant_admin') NOT NULL DEFAULT 'restaurant_admin',
    restaurant_id INT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE SET NULL,
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
