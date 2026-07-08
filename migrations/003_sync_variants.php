<?php
/**
 * Sync variants from JSON_DATA_START.txt into the database.
 * Finds items by en_name + category and adds/updates their variants.
 */
require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/Database.php';
require_once __DIR__ . '/../includes/helpers.php';

$db = Database::getInstance();

// 1. Read and parse the file
$filePath = __DIR__ . '/../JSON_DATA_START.txt';
if (!file_exists($filePath)) die("JSON_DATA_START.txt not found\n");

$content = file_get_contents($filePath);

// Extract the JSON array between "const menuData = [" and "];"
preg_match('/const menuData = (\[.*\]);/s', $content, $matches);
if (empty($matches[1])) die("Could not extract menuData array\n");

$menuData = json_decode($matches[1], true);
if (!is_array($menuData)) {
    // Try to fix common JS-to-JSON issues
    $json = $matches[1];
    $json = preg_replace('/,\s*]/', ']', $json); // Remove trailing commas
    $json = preg_replace('/,\s*}/', '}', $json);
    $menuData = json_decode($json, true);
}
if (!is_array($menuData)) die("JSON parse error: " . json_last_error_msg() . "\n");

echo "Parsed " . count($menuData) . " categories\n";

// 2. Get current restaurant
$restaurant = $db->query("SELECT id, slug FROM restaurants WHERE slug = 'lavina-house'")->fetch();
if (!$restaurant) die("Restaurant 'lavina-house' not found\n");
$restaurantId = $restaurant['id'];

$totalSynced = 0;
$totalSkipped = 0;

// 3. Process each category
foreach ($menuData as $catData) {
    $catNameEn = $catData['en_name'] ?? '';

    // Find matching category in DB
    $stmt = $db->prepare("SELECT id FROM categories WHERE restaurant_id = ? AND name_en = ?");
    $stmt->execute([$restaurantId, $catNameEn]);
    $cat = $stmt->fetch();
    if (!$cat) {
        echo "SKIP: Category not found: {$catNameEn}\n";
        continue;
    }
    $categoryId = $cat['id'];

    // Process direct items
    if (!empty($catData['items'])) {
        syncItems($db, $catData['items'], $categoryId, null, $totalSynced, $totalSkipped, $restaurantId);
    }

    // Process subcategories
    if (!empty($catData['subcategories'])) {
        foreach ($catData['subcategories'] as $subData) {
            $subNameEn = $subData['en_name'] ?? '';
            $stmt = $db->prepare("SELECT id FROM subcategories WHERE category_id = ? AND name_en = ?");
            $stmt->execute([$categoryId, $subNameEn]);
            $sub = $stmt->fetch();
            $subId = $sub ? $sub['id'] : null;

            if (!empty($subData['items'])) {
                syncItems($db, $subData['items'], $categoryId, $subId, $totalSynced, $totalSkipped, $restaurantId);
            }
        }
    }
}

echo "\n=== Done ===\n";
echo "Variants synced: {$totalSynced}\n";
echo "Items skipped (already had variants): {$totalSkipped}\n";

/**
 * Sync items and their variants with the database.
 */
function syncItems($db, $items, $categoryId, $subId, &$synced, &$skipped, $restaurantId) {
    foreach ($items as $itemData) {
        if (empty($itemData['variants']) || !is_array($itemData['variants'])) continue;

        $itemNameEn = $itemData['en_name'] ?? '';
        $itemNameAr = $itemData['name'] ?? '';

        // Find matching item in DB
        if ($subId) {
            $stmt = $db->prepare("SELECT id FROM items WHERE category_id = ? AND subcategory_id = ? AND en_name = ?");
            $stmt->execute([$categoryId, $subId, $itemNameEn]);
        } else {
            $stmt = $db->prepare("SELECT id FROM items WHERE category_id = ? AND subcategory_id IS NULL AND en_name = ?");
            $stmt->execute([$categoryId, $itemNameEn]);
        }
        $item = $stmt->fetch();

        if (!$item) {
            echo "  NOT FOUND: {$itemNameEn} (cat={$categoryId}, sub=" . ($subId ?? 'null') . ")\n";
            continue;
        }

        $itemId = $item['id'];

        // Check if item already has variants
        $existingCount = $db->prepare("SELECT COUNT(*) FROM variants WHERE item_id = ?");
        $existingCount->execute([$itemId]);
        $count = $existingCount->fetchColumn();

        if ($count > 0) {
            $skipped++;
            echo "  SKIP (already has {$count} variants): {$itemNameEn}\n";
            continue;
        }

        // Insert variants
        $sortOrder = 0;
        $inserted = 0;
        foreach ($itemData['variants'] as $varData) {
            $sortOrder++;

            // Handle inconsistent variant naming
            $varNameAr = $varData['name'] ?? $varData['variant_name'] ?? '';
            $varNameEn = $varData['en_name'] ?? $varData['variant_en_name'] ?? '';

            if (empty($varNameAr) && empty($varNameEn)) continue;

            $varPrice = null;
            if (!empty($varData['price'])) {
                $varPrice = parsePriceString($varData['price']);
            }

            $stmt = $db->prepare(
                "INSERT INTO variants (item_id, name_ar, name_en, price, desc_ar, desc_en, image, sort_order)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            );
            $stmt->execute([
                $itemId,
                $varNameAr,
                $varNameEn,
                $varPrice,
                $varData['desc'] ?? '',
                $varData['en_desc'] ?? '',
                $varData['image'] ?? null,
                $sortOrder
            ]);
            $inserted++;
        }

        if ($inserted > 0) {
            $synced++;
            echo "  SYNCED {$inserted} variants → {$itemNameEn}\n";
        }
    }
}
