<?php
/**
 * Admin API Router with authentication middleware.
 *
 * All admin endpoints go through here.
 * URL pattern: /admin/api/{endpoint}?action={action}&id={id}
 */

require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';

// Set headers
header('Access-Control-Allow-Origin: ' . APP_URL);
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-CSRF-Token');
header('Access-Control-Allow-Credentials: true');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// All admin endpoints require authentication
Auth::require();

// Get endpoint: try query param first (for direct calls), then URL path (for rewrites)
$endpoint = $_GET['endpoint'] ?? '';

if (empty($endpoint)) {
    $requestUri = $_SERVER['REQUEST_URI'] ?? '';
    $requestUri = preg_replace('/\?.*$/', '', $requestUri);
    $requestUri = trim($requestUri, '/');
    if (preg_match('#admin/api/([a-zA-Z_]+)#', $requestUri, $matches)) {
        $endpoint = $matches[1];
    }
}

// Route to handler
switch ($endpoint) {
    case 'auth':
        require_once __DIR__ . '/auth.php';
        handleAuth();
        break;

    case 'restaurants':
        require_once __DIR__ . '/restaurants.php';
        handleRestaurants();
        break;

    case 'categories':
        require_once __DIR__ . '/categories.php';
        handleCategories();
        break;

    case 'subcategories':
        require_once __DIR__ . '/subcategories.php';
        handleSubcategories();
        break;

    case 'items':
        require_once __DIR__ . '/items.php';
        handleItems();
        break;

    case 'variants':
        require_once __DIR__ . '/variants.php';
        handleVariants();
        break;

    case 'upload':
        require_once __DIR__ . '/upload.php';
        handleUpload();
        break;

    case 'admins':
        require_once __DIR__ . '/admins.php';
        handleAdmins();
        break;

    default:
        jsonError('Unknown admin endpoint', 404);
}
