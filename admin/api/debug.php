<?php
// Quick debug: test each layer
error_reporting(E_ALL);
ini_set('display_errors', '1');

echo "<h3>1. Loading config...</h3>";
require_once __DIR__ . '/../../includes/config.php';
echo "OK<br>DB: " . DB_NAME . "<br>";

echo "<h3>2. Loading Database.php...</h3>";
require_once __DIR__ . '/../../includes/Database.php';
echo "OK<br>";

echo "<h3>3. Connecting to MySQL...</h3>";
try {
    $db = Database::getInstance();
    echo "OK - Connected!<br>";

    $tables = $db->query("SHOW TABLES")->fetchAll(PDO::FETCH_COLUMN);
    echo "Tables found: " . count($tables) . "<br>";
    foreach ($tables as $t) echo "- $t<br>";

    echo "<h3>4. Testing query...</h3>";
    $stmt = $db->query("SELECT COUNT(*) FROM restaurants");
    echo "Restaurants: " . $stmt->fetchColumn() . "<br>";

    $stmt = $db->query("SELECT COUNT(*) FROM categories");
    echo "Categories: " . $stmt->fetchColumn() . "<br>";

} catch (Exception $e) {
    echo "<b style='color:red'>ERROR: " . $e->getMessage() . "</b><br>";
}

echo "<h3>5. Loading helpers.php...</h3>";
require_once __DIR__ . '/../../includes/helpers.php';
echo "OK<br>";

echo "<h3>6. Loading Auth.php...</h3>";
require_once __DIR__ . '/../../includes/Auth.php';
echo "OK<br>";

echo "<h3>7. Testing categories query...</h3>";
try {
    require_once __DIR__ . '/../../includes/helpers.php';
    $stmt = $db->prepare("SELECT * FROM categories WHERE restaurant_id = ? ORDER BY sort_order ASC");
    $stmt->execute([1]);
    $cats = $stmt->fetchAll();
    echo "Categories found: " . count($cats) . "<br>";
    foreach ($cats as $c) echo "- " . $c['name_en'] . " (id=" . $c['id'] . ")<br>";
    echo "<pre>" . json_encode($cats, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE) . "</pre>";
} catch (Exception $e) {
    echo "<b style='color:red'>ERROR: " . $e->getMessage() . "</b><br>";
}

echo "<h3>Done!</h3>";
