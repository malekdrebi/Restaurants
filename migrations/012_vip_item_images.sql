CREATE TABLE vip_item_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vip_item_id INT NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    sort_order INT DEFAULT 0,
    FOREIGN KEY (vip_item_id) REFERENCES vip_items(id) ON DELETE CASCADE,
    INDEX idx_vip_item (vip_item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
