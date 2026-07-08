<?php
/**
 * Migration: Seed Lavina House restaurant from the_menu_bilingual.json
 *
 * Run once to migrate existing menu data into the MySQL database.
 * Usage: php migrations/002_seed_lavina.php
 */

require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/Database.php';
require_once __DIR__ . '/../includes/helpers.php';

$db = Database::getInstance();
$jsonPath = __DIR__ . '/../the_menu_bilingual.json';

if (!file_exists($jsonPath)) {
    die("ERROR: the_menu_bilingual.json not found at $jsonPath\n");
}

$json = file_get_contents($jsonPath);
$menuData = json_decode($json, true);

if (!is_array($menuData)) {
    die("ERROR: Failed to parse JSON. Error: " . json_last_error_msg() . "\n");
}

echo "=== Seeding Lavina House Restaurant ===\n\n";

// ─── 1. Create Restaurant ───────────────────────────────────────
echo "[1/7] Creating restaurant...\n";
$stmt = $db->prepare("INSERT INTO restaurants (slug, name_ar, name_en, is_active, sort_order) VALUES (?, ?, ?, 1, 0)");
$stmt->execute(['lavina-house', 'ﻻﻓﻴﻨﺎ هاوس', 'Lavina House']);
$restaurantId = (int) $db->lastInsertId();
echo "  ✓ Restaurant #{$restaurantId}: Lavina House (slug: lavina-house)\n\n";

// ─── 2. Create Default Admin ────────────────────────────────────
echo "[2/7] Creating default admin...\n";
$passwordHash = password_hash('lavina2024', PASSWORD_BCRYPT);
$stmt = $db->prepare("INSERT INTO admins (username, password_hash, role, restaurant_id) VALUES (?, ?, 'super_admin', NULL)");
$stmt->execute(['admin', $passwordHash]);
echo "  ✓ Super admin created (username: admin, password: lavina2024)\n";
echo "  ⚠ CHANGE THE PASSWORD AFTER FIRST LOGIN!\n\n";

// ─── 3. Process Categories & Items ──────────────────────────────
echo "[3/7] Processing menu data...\n";

$categorySortOrder = 0;
$totalItems = 0;
$totalVariants = 0;
$totalSubcategories = 0;

foreach ($menuData as $catData) {
    $categorySortOrder++;

    // Determine if this is a featured category
    $isFeatured = 0;
    $featuredType = null;
    if ($catData['en_name'] === 'Most Ordered') {
        $isFeatured = 1;
        $featuredType = 'most_ordered';
    } elseif ($catData['en_name'] === 'Fastest Ordered') {
        $isFeatured = 1;
        $featuredType = 'fastest_ordered';
    }

    // Insert category
    $stmt = $db->prepare(
        "INSERT INTO categories (restaurant_id, name_ar, name_en, image, is_featured, featured_type, sort_order)
         VALUES (?, ?, ?, ?, ?, ?, ?)"
    );
    $stmt->execute([
        $restaurantId,
        $catData['name'] ?? '',
        $catData['en_name'] ?? '',
        isset($catData['image']) && $catData['image'] !== '' ? $catData['image'] : null,
        $isFeatured,
        $featuredType,
        $categorySortOrder
    ]);
    $categoryId = (int) $db->lastInsertId();

    $hasSubcategories = !empty($catData['subcategories']);
    $hasDirectItems = !empty($catData['items']);

    // Insert direct items (no subcategory)
    if ($hasDirectItems && is_array($catData['items'])) {
        insertItems($db, $catData['items'], $categoryId, null, $totalItems, $totalVariants);
    }

    // Insert subcategories and their items
    if ($hasSubcategories && is_array($catData['subcategories'])) {
        $subSortOrder = 0;
        foreach ($catData['subcategories'] as $subData) {
            $subSortOrder++;
            $stmt = $db->prepare(
                "INSERT INTO subcategories (category_id, name_ar, name_en, sort_order)
                 VALUES (?, ?, ?, ?)"
            );
            $stmt->execute([
                $categoryId,
                $subData['name'] ?? '',
                $subData['en_name'] ?? '',
                $subSortOrder
            ]);
            $subcategoryId = (int) $db->lastInsertId();
            $totalSubcategories++;

            if (!empty($subData['items']) && is_array($subData['items'])) {
                insertItems($db, $subData['items'], $categoryId, $subcategoryId, $totalItems, $totalVariants);
            }
        }
    }

    echo "  ✓ {$catData['en_name']}: " . ($hasSubcategories ? count($catData['subcategories']) . ' subcategories, ' : '') . ($hasDirectItems ? count($catData['items']) . ' items' : '') . "\n";
}

echo "\n  Totals: {$totalItems} items, {$totalVariants} variants, {$totalSubcategories} subcategories\n\n";

// ─── 4. Copy & Normalize Images ─────────────────────────────────
echo "[4/7] Processing images...\n";
$imagesDir = __DIR__ . '/../images/lavina-house/items';
ensureDir($imagesDir);

$copied = 0;
$missing = 0;
$skipped = 0;

// Scan for all image references in the database and copy them
$stmt = $db->query("SELECT id, image FROM items WHERE image IS NOT NULL AND image != ''");
$itemImages = $stmt->fetchAll();

foreach ($itemImages as $row) {
    $oldPath = __DIR__ . '/../' . $row['image'];

    // Try multiple filename variations (handle inconsistent naming)
    $foundPath = findImageFile($oldPath);

    if ($foundPath) {
        $ext = strtolower(pathinfo($foundPath, PATHINFO_EXTENSION));
        $newName = 'item_' . $row['id'] . '.' . $ext;
        $newPath = $imagesDir . '/' . $newName;

        if (copy($foundPath, $newPath)) {
            // Update the DB with the new clean path
            $newRelPath = 'images/lavina-house/items/' . $newName;
            $stmt = $db->prepare("UPDATE items SET image = ? WHERE id = ?");
            $stmt->execute([$newRelPath, $row['id']]);
            $copied++;
        }
    } else {
        // Clear the image reference if the file doesn't exist
        $stmt = $db->prepare("UPDATE items SET image = NULL WHERE id = ?");
        $stmt->execute([$row['id']]);
        $missing++;
    }
}

echo "  ✓ Images copied: {$copied}\n";
echo "  ✓ Missing (cleared): {$missing}\n\n";

// ─── 5. Verify Counts ───────────────────────────────────────────
echo "[5/7] Verifying data integrity...\n";
$itemCount = $db->query("SELECT COUNT(*) FROM items")->fetchColumn();
$variantCount = $db->query("SELECT COUNT(*) FROM variants")->fetchColumn();
$catCount = $db->query("SELECT COUNT(*) FROM categories")->fetchColumn();
$subcatCount = $db->query("SELECT COUNT(*) FROM subcategories")->fetchColumn();
echo "  Database: {$catCount} categories, {$subcatCount} subcategories, {$itemCount} items, {$variantCount} variants\n";
echo "  JSON: " . count($menuData) . " top-level categories\n\n";

echo "\n[6/6] Migration complete!\n";
echo "═══════════════════════════════════════════\n";
echo "  Admin URL:  /admin/index.html\n";
echo "  Username:   admin\n";
echo "  Password:   lavina2024\n";
echo "  Menu URL:   /menu?slug=lavina-house\n";
echo "═══════════════════════════════════════════\n";

// ═════════════════════════════════════════════════════════════════
// Helper Functions
// ═════════════════════════════════════════════════════════════════

/**
 * Insert items and their variants into the database.
 */
function insertItems(PDO $db, array $items, int $categoryId, ?int $subcategoryId, int &$totalItems, int &$totalVariants): void
{
    $itemSort = 0;
    $itemStmt = $db->prepare(
        "INSERT INTO items (category_id, subcategory_id, name_ar, name_en, price, desc_ar, desc_en, image, sort_order)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    );
    $variantStmt = $db->prepare(
        "INSERT INTO variants (item_id, name_ar, name_en, price, desc_ar, desc_en, image, sort_order)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    );

    foreach ($items as $itemData) {
        $itemSort++;

        $price = parsePriceString($itemData['price'] ?? '0 د.ل');
        $image = (!empty($itemData['image'])) ? $itemData['image'] : null;

        $itemStmt->execute([
            $categoryId,
            $subcategoryId,
            $itemData['name'] ?? '',
            $itemData['en_name'] ?? '',
            $price,
            $itemData['desc'] ?? '',
            $itemData['en_desc'] ?? '',
            $image,
            $itemSort
        ]);
        $itemId = (int) $db->lastInsertId();
        $totalItems++;

        // Insert variants if present
        if (!empty($itemData['variants']) && is_array($itemData['variants'])) {
            $varSort = 0;
            foreach ($itemData['variants'] as $varData) {
                $varSort++;

                // Handle inconsistent variant naming
                $varNameAr = $varData['variant_name'] ?? $varData['name'] ?? '';
                $varNameEn = $varData['variant_en_name'] ?? $varData['en_name'] ?? '';

                // Variant price: if empty or not set, use parent price
                $varPrice = null;
                if (!empty($varData['price'])) {
                    $varPrice = parsePriceString($varData['price']);
                }

                $varImage = (!empty($varData['image'])) ? $varData['image'] : null;
                $varDescAr = $varData['desc'] ?? '';
                $varDescEn = $varData['en_desc'] ?? '';

                // Skip variants that are identical to their parent or empty
                // (Some items have variants arrays with empty variant objects)
                if (empty($varNameAr) && empty($varNameEn)) {
                    continue;
                }

                $variantStmt->execute([
                    $itemId,
                    $varNameAr,
                    $varNameEn,
                    $varPrice,
                    $varDescAr,
                    $varDescEn,
                    $varImage,
                    $varSort
                ]);
                $totalVariants++;
            }
        }
    }
}

/**
 * Try to find an image file given its referenced path.
 * Handles mismatched filenames (Arabic vs English vs PascalCase vs snake_case).
 */
function findImageFile(string $referencedPath): ?string
{
    // 1. Try the exact path as referenced
    if (file_exists($referencedPath)) {
        return $referencedPath;
    }

    // 2. Extract the filename and try variations
    $dir = dirname($referencedPath);
    $filename = basename($referencedPath);

    // If directory doesn't exist, try the root images dir
    if (!is_dir($dir)) {
        $dir = __DIR__ . '/../images';
    }

    // Check if the directory has files
    if (!is_dir($dir)) {
        return null;
    }

    $files = scandir($dir);
    if ($files === false) {
        return null;
    }

    $baseWithoutExt = strtolower(pathinfo($filename, PATHINFO_FILENAME));

    // 3. Case-insensitive match in the same directory
    foreach ($files as $file) {
        if ($file === '.' || $file === '..') continue;
        $checkBase = strtolower(pathinfo($file, PATHINFO_FILENAME));
        if ($checkBase === $baseWithoutExt) {
            return $dir . '/' . $file;
        }
    }

    // 4. Try slugified version in images/
    $slugDir = __DIR__ . '/../images';
    if ($slugDir !== $dir && is_dir($slugDir)) {
        $slugFiles = scandir($slugDir);
        if ($slugFiles !== false) {
            foreach ($slugFiles as $file) {
                if ($file === '.' || $file === '..') continue;
                $checkBase = strtolower(pathinfo($file, PATHINFO_FILENAME));
                if ($checkBase === $baseWithoutExt) {
                    return $slugDir . '/' . $file;
                }
            }
        }
    }

    return null;
}
