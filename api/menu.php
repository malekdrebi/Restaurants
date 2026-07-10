<?php
/**
 * Menu API — Returns the full menu for a restaurant.
 *
 * Response format matches the original menuData JS structure
 * so the customer-facing menu.html needs minimal changes.
 */

function getMenuData(PDO $db, string $slug): ?array
{
    // 1. Get restaurant
    $stmt = $db->prepare(
        "SELECT id, slug, name_ar, name_en, logo, bg_image, primary_color, show_vip, show_gallery, show_tutorial, show_cart, show_parallax, show_hub, show_vip_prices, address_ar, address_en, phone, maps_url
         FROM restaurants WHERE slug = ? AND is_active = 1"
    );
    $stmt->execute([$slug]);
    $restaurant = $stmt->fetch();

    if (!$restaurant) {
        return null;
    }

    // 2. Get categories with their items and subcategories
    $stmt = $db->prepare(
        "SELECT * FROM categories WHERE restaurant_id = ? ORDER BY sort_order ASC"
    );
    $stmt->execute([$restaurant['id']]);
    $categories = $stmt->fetchAll();

    $menu = [];

    foreach ($categories as $cat) {
        $categoryData = [
            'id'   => (int) $cat['id'],
            'name' => $cat['name_ar'],
            'en_name' => $cat['name_en'],
            'image' => $cat['image'],
            'is_featured' => (bool) $cat['is_featured'],
            'featured_type' => $cat['featured_type'],
        ];

        // 3. Get subcategories for this category
        $stmt = $db->prepare(
            "SELECT * FROM subcategories WHERE category_id = ? ORDER BY sort_order ASC"
        );
        $stmt->execute([$cat['id']]);
        $subcategories = $stmt->fetchAll();

        if (count($subcategories) > 0) {
            $categoryData['subcategories'] = [];

            foreach ($subcategories as $sub) {
                $subData = [
                    'name' => $sub['name_ar'],
                    'en_name' => $sub['name_en'],
                    'items' => getItems($db, $cat['id'], $sub['id']),
                ];
                $categoryData['subcategories'][] = $subData;
            }

            // Also get items directly under this category (not in any subcategory)
            $directItems = getItems($db, $cat['id'], null);
            if (count($directItems) > 0) {
                $categoryData['items'] = $directItems;
            }
        } else {
            // No subcategories — just direct items
            $categoryData['items'] = getItems($db, $cat['id'], null);
        }

        $menu[] = $categoryData;
    }

    // Get gallery images for this restaurant
    $gStmt = $db->prepare("SELECT image_path FROM gallery_images WHERE restaurant_id = ? ORDER BY sort_order ASC");
    $gStmt->execute([$restaurant['id']]);
    $gallery = $gStmt->fetchAll(PDO::FETCH_COLUMN);

    // Get VIP items for this restaurant
    $vStmt = $db->prepare("SELECT * FROM vip_items WHERE restaurant_id = ? ORDER BY sort_order ASC");
    $vStmt->execute([$restaurant['id']]);
    $vipItems = $vStmt->fetchAll();

    return [
        'restaurant' => [
            'slug'    => $restaurant['slug'],
            'name_ar' => $restaurant['name_ar'],
            'name_en' => $restaurant['name_en'],
            'logo'    => $restaurant['logo'],
            'bg_image' => $restaurant['bg_image'],
            'primary_color' => $restaurant['primary_color'],
            'show_vip' => (bool)$restaurant['show_vip'],
            'show_gallery' => (bool)$restaurant['show_gallery'],
            'show_tutorial' => (bool)$restaurant['show_tutorial'],
            'show_cart' => (bool)$restaurant['show_cart'],
            'show_parallax' => (bool)$restaurant['show_parallax'],
            'show_hub' => (bool)$restaurant['show_hub'],
            'show_vip_prices' => (bool)$restaurant['show_vip_prices'],
            'address_ar' => $restaurant['address_ar'],
            'address_en' => $restaurant['address_en'],
            'phone'   => $restaurant['phone'],
            'maps_url' => $restaurant['maps_url'],
        ],
        'menu' => $menu,
        'gallery' => $gallery,
        'vip_items' => $vipItems,
    ];
}

/**
 * Get items for a category/subcategory, including their variants.
 */
function getItems(PDO $db, int $categoryId, ?int $subcategoryId): array
{
    if ($subcategoryId !== null) {
        $stmt = $db->prepare(
            "SELECT * FROM items
             WHERE category_id = ? AND subcategory_id = ?
             ORDER BY sort_order ASC"
        );
        $stmt->execute([$categoryId, $subcategoryId]);
    } else {
        $stmt = $db->prepare(
            "SELECT * FROM items
             WHERE category_id = ? AND subcategory_id IS NULL
             ORDER BY sort_order ASC"
        );
        $stmt->execute([$categoryId]);
    }

    $items = $stmt->fetchAll();
    $result = [];

    foreach ($items as $item) {
        $itemData = [
            'id'          => (int) $item['id'],
            'name'        => $item['name_ar'],
            'en_name'     => $item['name_en'],
            'price'       => formatPrice((float) $item['price'], 'ar'),
            'price_en'    => formatPrice((float) $item['price'], 'en'),
            'desc'        => $item['desc_ar'] ?? '',
            'en_desc'     => $item['desc_en'] ?? '',
            'image'       => $item['image'],
            'spicy'       => (bool) $item['spicy'],
            'recommended' => (bool) $item['recommended'],
        ];

        // Get variants for this item
        $vStmt = $db->prepare(
            "SELECT * FROM variants WHERE item_id = ? ORDER BY sort_order ASC"
        );
        $vStmt->execute([$item['id']]);
        $variants = $vStmt->fetchAll();

        if (count($variants) > 0) {
            $itemData['variants'] = [];
            foreach ($variants as $var) {
                $varPrice = $var['price'] !== null ? (float) $var['price'] : (float) $item['price'];
                $itemData['variants'][] = [
                    'id'       => (int) $var['id'],
                    'name'     => $var['name_ar'],
                    'en_name'  => $var['name_en'],
                    'price'    => formatPrice($varPrice, 'ar'),
                    'price_en' => formatPrice($varPrice, 'en'),
                    'desc'     => $var['desc_ar'] ?? '',
                    'en_desc'  => $var['desc_en'] ?? '',
                    'image'    => $var['image'],
                ];
            }
        }

        $result[] = $itemData;
    }

    return $result;
}
