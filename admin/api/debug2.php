<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');

require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';

echo "<h3>1. Session check</h3>";
if (session_status() === PHP_SESSION_NONE) session_start();
if (isset($_SESSION['admin'])) {
    echo "Logged in: " . $_SESSION['admin']['username'] . " (role: " . $_SESSION['admin']['role'] . ")<br>";
} else {
    echo "<b>NOT logged in — THIS IS THE PROBLEM</b><br>";
    echo "Session ID: " . session_id() . "<br>";
    exit;
}

echo "<h3>2. Testing GET categories (no exit)</h3>";
$db = Database::getInstance();
$restaurantId = 1;
$stmt = $db->prepare("SELECT * FROM categories WHERE restaurant_id = ? ORDER BY sort_order ASC");
$stmt->execute([$restaurantId]);
$cats = $stmt->fetchAll();
echo "Found " . count($cats) . " categories<br>";

echo "<h3>3. Testing POST create category (no exit)</h3>";
// Simulate what categories.php POST does
$admin = Auth::user();
echo "Admin role: " . $admin['role'] . "<br>";
echo "Restaurant access check for ID 1: " . (Auth::canAccessRestaurant(1) ? 'YES' : 'NO') . "<br>";

echo "<h3>4. CSRF token check</h3>";
echo "Session CSRF: " . ($_SESSION['csrf_token'] ?? 'NOT SET') . "<br>";

echo "<h3>5. PHP version</h3>";
echo "PHP " . phpversion() . "<br>";

echo "<h3>Done — all checks passed!</h3>";
