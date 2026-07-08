<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');

echo "<pre>--- TESTING ROUTER FLOW ---\n";

echo "1. Loading includes...\n";
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';
echo "OK\n";

echo "2. Auth check...\n";
try {
    Auth::require();
    echo "OK - Authenticated\n";
} catch (Throwable $e) {
    echo "AUTH FAILED: " . $e->getMessage() . "\n";
    exit;
}

echo "3. Endpoint: " . ($_GET['endpoint'] ?? 'none') . "\n";

echo "4. Loading categories.php...\n";
require_once __DIR__ . '/categories.php';
echo "OK\n";

echo "5. Calling GET handler manually...\n";

$method = 'GET';
$restaurantId = (int) ($_GET['restaurant_id'] ?? 0);
echo "   restaurant_id=$restaurantId\n";

if (!$restaurantId) {
    echo "   ERROR: restaurant_id is required\n";
    exit;
}

Auth::requireRestaurantAccess($restaurantId);
echo "   Access OK\n";

$db = Database::getInstance();
$stmt = $db->prepare("SELECT * FROM categories WHERE restaurant_id = ? ORDER BY sort_order ASC");
$stmt->execute([$restaurantId]);
$cats = $stmt->fetchAll();
echo "   Found " . count($cats) . " categories\n";
echo "   SUCCESS\n";
echo "</pre>";
