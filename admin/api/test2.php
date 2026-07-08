<?php
error_reporting(E_ALL);
ini_set('display_errors', '1');

require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';
require_once __DIR__ . '/categories.php';

echo "Calling handleCategories()...\n";
// Use output buffering to catch the response
ob_start();
handleCategories();
$output = ob_get_clean();
echo "Function returned!\n";
echo "Output: " . $output . "\n";
