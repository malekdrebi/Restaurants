ALTER TABLE restaurants
  ADD COLUMN primary_color VARCHAR(7) DEFAULT '#C9A366' AFTER bg_image,
  ADD COLUMN show_vip TINYINT(1) DEFAULT 1 AFTER primary_color,
  ADD COLUMN show_gallery TINYINT(1) DEFAULT 1 AFTER show_vip,
  ADD COLUMN show_tutorial TINYINT(1) DEFAULT 1 AFTER show_gallery,
  ADD COLUMN show_cart TINYINT(1) DEFAULT 1 AFTER show_tutorial,
  ADD COLUMN show_parallax TINYINT(1) DEFAULT 1 AFTER show_cart,
  ADD COLUMN show_hub TINYINT(1) DEFAULT 1 AFTER show_parallax;
