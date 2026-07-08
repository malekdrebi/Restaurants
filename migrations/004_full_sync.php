<?php
/**
 * Full sync: import all items+variants from the_menu_updated.json.
 * Creates missing items and categories. Skips existing items with variants.
 */
require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/Database.php';
require_once __DIR__ . '/../includes/helpers.php';

set_time_limit(300);
ini_set('memory_limit', '512M');
ini_set('display_errors', '1');
error_reporting(E_ALL);
ob_implicit_flush(true);
@ob_end_flush();

$db = Database::getInstance();

$json = json_decode(file_get_contents(__DIR__ . '/../the_menu_updated.json'), true);
if (!$json) die("JSON parse error\n");

$restaurant = $db->query("SELECT id FROM restaurants WHERE slug='lavina-house'")->fetch();
$restaurantId = $restaurant['id'];

echo "Full sync — will create missing items & categories\n\n";

$created = 0; $varianted = 0; $skipped = 0;

// Process each category in the JSON
foreach ($json as $catData) {
    $catNameEn = trim($catData['en_name'] ?? '');
    $catNameAr = trim($catData['name'] ?? '');

    // Find or create category
    $stmt = $db->prepare("SELECT id FROM categories WHERE restaurant_id=? AND name_en=?");
    $stmt->execute([$restaurantId, $catNameEn]);
    $cat = $stmt->fetch();
    if (!$cat) {
        // Try Arabic name
        $stmt = $db->prepare("SELECT id FROM categories WHERE restaurant_id=? AND name_ar=?");
        $stmt->execute([$restaurantId, $catNameAr]);
        $cat = $stmt->fetch();
    }
    if (!$cat) {
        // CREATE missing category
        $sortOrder = $db->query("SELECT MAX(sort_order)+1 FROM categories WHERE restaurant_id=$restaurantId")->fetchColumn() ?: 1;
        $db->prepare("INSERT INTO categories (restaurant_id,name_ar,name_en,sort_order) VALUES (?,?,?,?)")
           ->execute([$restaurantId, $catNameAr, $catNameEn, $sortOrder]);
        $cat = ['id' => $db->lastInsertId()];
        echo "CREATED category: {$catNameEn} (id={$cat['id']})\n";
    }

    // Process direct items
    if (!empty($catData['items'])) {
        processItems($db, $catData['items'], $cat['id'], null, $restaurantId, $created, $varianted, $skipped);
    }

    // Process subcategories
    if (!empty($catData['subcategories'])) {
        foreach ($catData['subcategories'] as $subData) {
            $subNameEn = trim($subData['en_name'] ?? '');
            $subNameAr = trim($subData['name'] ?? '');
            $stmt = $db->prepare("SELECT id FROM subcategories WHERE category_id=? AND name_en=?");
            $stmt->execute([$cat['id'], $subNameEn]);
            $sub = $stmt->fetch();
            if (!$sub) {
                $sortOrder = $db->prepare("SELECT MAX(sort_order)+1 FROM subcategories WHERE category_id=?");
                $sortOrder->execute([$cat['id']]);
                $so = $sortOrder->fetchColumn() ?: 1;
                $db->prepare("INSERT INTO subcategories (category_id,name_ar,name_en,sort_order) VALUES (?,?,?,?)")
                   ->execute([$cat['id'], $subNameAr, $subNameEn, $so]);
                $sub = ['id' => $db->lastInsertId()];
                echo "  CREATED subcategory: {$subNameEn}\n";
            }
            if (!empty($subData['items'])) {
                processItems($db, $subData['items'], $cat['id'], $sub['id'], $restaurantId, $created, $varianted, $skipped);
            }
        }
    }
}

echo "\n=== Done ===\n";
echo "Items created: {$created}\n";
echo "Items given variants: {$varianted}\n";
echo "Items skipped (already had variants): {$skipped}\n";

function processItems($db, $items, $catId, $subId, $restId, &$created, &$varianted, &$skipped) {
    foreach ($items as $itemData) {
        $nameEn = trim($itemData['en_name'] ?? '');
        $nameAr = trim($itemData['name'] ?? '');
        if (empty($nameEn)) continue;

        // Find existing item
        if ($subId) {
            $stmt = $db->prepare("SELECT id FROM items WHERE category_id=? AND subcategory_id=? AND name_en=?");
            $stmt->execute([$catId, $subId, $nameEn]);
        } else {
            $stmt = $db->prepare("SELECT id FROM items WHERE category_id=? AND subcategory_id IS NULL AND name_en=?");
            $stmt->execute([$catId, $nameEn]);
        }
        $item = $stmt->fetch();

        // If not found, CREATE the item
        if (!$item) {
            $price = parsePriceString($itemData['price'] ?? '0');
            $descAr = $itemData['desc'] ?? '';
            $descEn = $itemData['en_desc'] ?? '';
            $image = !empty($itemData['image']) ? $itemData['image'] : null;
            $sortOrder = $db->prepare(
                "SELECT MAX(sort_order)+1 FROM items WHERE category_id=? AND " . ($subId ? "subcategory_id=?" : "subcategory_id IS NULL")
            );
            if ($subId) $sortOrder->execute([$catId, $subId]);
            else $sortOrder->execute([$catId]);
            $so = $sortOrder->fetchColumn() ?: 1;

            $db->prepare("INSERT INTO items (category_id,subcategory_id,name_ar,name_en,price,desc_ar,desc_en,image,sort_order) VALUES (?,?,?,?,?,?,?,?,?)")
               ->execute([$catId, $subId, $nameAr, $nameEn, $price, $descAr, $descEn, $image, $so]);
            $item = ['id' => $db->lastInsertId()];
            $created++;
            echo "  CREATED item: {$nameEn}\n";
        }

        // Add variants if item has them and doesn't already
        if (!empty($itemData['variants']) && is_array($itemData['variants'])) {
            $vCount = $db->prepare("SELECT COUNT(*) FROM variants WHERE item_id=?");
            $vCount->execute([$item['id']]);
            if ($vCount->fetchColumn() > 0) {
                $skipped++;
                continue;
            }
            $sort = 0;
            $added = 0;
            foreach ($itemData['variants'] as $v) {
                $sort++;
                $vAr = $v['name'] ?? $v['variant_name'] ?? '';
                $vEn = $v['en_name'] ?? $v['variant_en_name'] ?? '';
                if (empty($vAr) && empty($vEn)) continue;
                $vPrice = !empty($v['price']) ? parsePriceString($v['price']) : null;
                $db->prepare("INSERT INTO variants (item_id,name_ar,name_en,price,desc_ar,desc_en,image,sort_order) VALUES (?,?,?,?,?,?,?,?)")
                   ->execute([$item['id'], $vAr, $vEn, $vPrice, $v['desc'] ?? '', $v['en_desc'] ?? '', $v['image'] ?? null, $sort]);
                $added++;
            }
            if ($added > 0) {
                $varianted++;
                echo "    +{$added} variants\n";
            }
        }
    }
}
