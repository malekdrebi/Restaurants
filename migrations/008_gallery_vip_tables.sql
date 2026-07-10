CREATE TABLE gallery_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_restaurant (restaurant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE vip_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    title_ar VARCHAR(255) NOT NULL,
    title_en VARCHAR(255) NOT NULL,
    desc_ar TEXT,
    desc_en TEXT,
    price VARCHAR(50),
    image_path VARCHAR(255),
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    INDEX idx_restaurant (restaurant_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed Lavina House gallery from existing look/ folder
INSERT INTO gallery_images (restaurant_id, image_path, sort_order)
SELECT id, 'look/1.jpg', 1 FROM restaurants WHERE slug='lavina-house';
INSERT INTO gallery_images (restaurant_id, image_path, sort_order)
SELECT id, 'look/2.jpg', 2 FROM restaurants WHERE slug='lavina-house';
INSERT INTO gallery_images (restaurant_id, image_path, sort_order)
SELECT id, 'look/3.jpg', 3 FROM restaurants WHERE slug='lavina-house';
INSERT INTO gallery_images (restaurant_id, image_path, sort_order)
SELECT id, 'look/4.jpg', 4 FROM restaurants WHERE slug='lavina-house';
INSERT INTO gallery_images (restaurant_id, image_path, sort_order)
SELECT id, 'look/5.jpg', 5 FROM restaurants WHERE slug='lavina-house';
INSERT INTO gallery_images (restaurant_id, image_path, sort_order)
SELECT id, 'look/7.jpg', 6 FROM restaurants WHERE slug='lavina-house';
INSERT INTO gallery_images (restaurant_id, image_path, sort_order)
SELECT id, 'look/8.jpg', 7 FROM restaurants WHERE slug='lavina-house';
INSERT INTO gallery_images (restaurant_id, image_path, sort_order)
SELECT id, 'look/9.jpg', 8 FROM restaurants WHERE slug='lavina-house';
INSERT INTO gallery_images (restaurant_id, image_path, sort_order)
SELECT id, 'look/10.jpg', 9 FROM restaurants WHERE slug='lavina-house';
INSERT INTO gallery_images (restaurant_id, image_path, sort_order)
SELECT id, 'look/11.jpg', 10 FROM restaurants WHERE slug='lavina-house';

-- Seed Lavina House VIP from existing vip/ folder
INSERT INTO vip_items (restaurant_id, title_ar, title_en, desc_ar, desc_en, price, image_path, sort_order)
SELECT id, 'بوفيه مفتوح', 'Open Buffet', 'تشكيلة واسعة من الأطباق العالمية', 'Wide selection of international dishes', '150 د.ل', 'vip/1.jpg', 1 FROM restaurants WHERE slug='lavina-house';
INSERT INTO vip_items (restaurant_id, title_ar, title_en, desc_ar, desc_en, price, image_path, sort_order)
SELECT id, 'منيو مخصص', 'Set Menu', 'قائمة مصممة خصيصاً لمناسبتك', 'Custom designed menu for your event', '200 د.ل', 'vip/2.jpg', 2 FROM restaurants WHERE slug='lavina-house';
