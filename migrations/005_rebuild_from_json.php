<?php
/**
 * REBUILD: Delete all existing data for restaurant #1 and re-import from the_menu_updated.json.
 * This ensures the DB matches the JSON file exactly — items with variants become one item with variants.
 */
require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/Database.php';
require_once __DIR__ . '/../includes/helpers.php';

set_time_limit(300); ini_set('memory_limit', '512M');
ini_set('display_errors', '1'); error_reporting(E_ALL);
ob_implicit_flush(true); @ob_end_flush();

$db = Database::getInstance();
$restaurantId = 1;

$json = json_decode(file_get_contents(__DIR__ . '/../the_menu_updated.json'), true);
if (!$json) die("JSON parse error: " . json_last_error_msg() . "\n");

echo "=== REBUILDING RESTAURANT #1 FROM JSON ===\n\n";

// 1. DELETE all existing data
echo "Deleting existing data...\n";
$db->exec("DELETE FROM variants WHERE item_id IN (SELECT id FROM items WHERE category_id IN (SELECT id FROM categories WHERE restaurant_id=$restaurantId))");
$db->exec("DELETE FROM items WHERE category_id IN (SELECT id FROM categories WHERE restaurant_id=$restaurantId)");
$db->exec("DELETE FROM subcategories WHERE category_id IN (SELECT id FROM categories WHERE restaurant_id=$restaurantId)");
$db->exec("DELETE FROM categories WHERE restaurant_id=$restaurantId");
echo "Cleared.\n\n";

// 2. IMPORT fresh
$catSort = 0;
$totalItems = 0; $totalVariants = 0; $totalSubs = 0; $totalCats = 0;

foreach ($json as $catData) {
    $catSort++;
    $catNameEn = trim($catData['en_name'] ?? '');
    $catNameAr = trim($catData['name'] ?? '');
    if (empty($catNameEn)) continue;

    $isFeatured = ($catNameEn === 'Most Ordered') ? 1 : (($catNameEn === 'Fastest Ordered') ? 1 : 0);
    $ft = ($catNameEn === 'Most Ordered') ? 'most_ordered' : (($catNameEn === 'Fastest Ordered') ? 'fastest_ordered' : null);

    $db->prepare("INSERT INTO categories (restaurant_id,name_ar,name_en,is_featured,featured_type,sort_order) VALUES (?,?,?,?,?,?)")
       ->execute([$restaurantId, $catNameAr, $catNameEn, $isFeatured, $ft, $catSort]);
    $catId = $db->lastInsertId();
    $totalCats++;
    echo "Category: {$catNameEn} (id={$catId})\n";

    // Direct items
    if (!empty($catData['items'])) {
        insertItems($db, $catData['items'], $catId, null, $totalItems, $totalVariants);
    }

    // Subcategories
    if (!empty($catData['subcategories'])) {
        $subSort = 0;
        foreach ($catData['subcategories'] as $subData) {
            $subSort++;
            $subNameEn = trim($subData['en_name'] ?? '');
            $subNameAr = trim($subData['name'] ?? '');
            if (empty($subNameEn)) continue;

            $db->prepare("INSERT INTO subcategories (category_id,name_ar,name_en,sort_order) VALUES (?,?,?,?)")
               ->execute([$catId, $subNameAr, $subNameEn, $subSort]);
            $subId = $db->lastInsertId();
            $totalSubs++;

            if (!empty($subData['items'])) {
                insertItems($db, $subData['items'], $catId, $subId, $totalItems, $totalVariants);
            }
        }
    }
}

echo "\n=== DONE ===\n";
echo "Categories: {$totalCats}\n";
echo "Subcategories: {$totalSubs}\n";
echo "Items: {$totalItems}\n";
echo "Variants: {$totalVariants}\n";

function insertItems($db, $items, $catId, $subId, &$totalItems, &$totalVariants) {
    $sort = 0;
    foreach ($items as $item) {
        $sort++;
        $nameEn = trim($item['en_name'] ?? '');
        $nameAr = trim($item['name'] ?? '');
        if (empty($nameEn) && empty($nameAr)) continue;

        $price = parsePriceString($item['price'] ?? '0');
        $descAr = $item['desc'] ?? '';
        $descEn = $item['en_desc'] ?? '';
        $image = !empty($item['image']) ? $item['image'] : null;

        $db->prepare("INSERT INTO items (category_id,subcategory_id,name_ar,name_en,price,desc_ar,desc_en,image,sort_order) VALUES (?,?,?,?,?,?,?,?,?)")
           ->execute([$catId, $subId, $nameAr, $nameEn, $price, $descAr, $descEn, $image, $sort]);
        $itemId = $db->lastInsertId();
        $totalItems++;

        // Variants
        if (!empty($item['variants']) && is_array($item['variants'])) {
            $vSort = 0;
            foreach ($item['variants'] as $v) {
                $vSort++;
                $vAr = trim($v['name'] ?? $v['variant_name'] ?? '');
                $vEn = trim($v['en_name'] ?? $v['variant_en_name'] ?? '');
                if (empty($vAr) && empty($vEn)) continue;
                $vPrice = !empty($v['price']) ? parsePriceString($v['price']) : null;
                $vDescAr = $v['desc'] ?? '';
                $vDescEn = $v['en_desc'] ?? '';
                $vImage = !empty($v['image']) ? $v['image'] : null;

                $db->prepare("INSERT INTO variants (item_id,name_ar,name_en,price,desc_ar,desc_en,image,sort_order) VALUES (?,?,?,?,?,?,?,?)")
                   ->execute([$itemId, $vAr, $vEn, $vPrice, $vDescAr, $vDescEn, $vImage, $vSort]);
                $totalVariants++;
            }
        }
    }
}
