<?php
/**
 * Public API Router
 *
 * Handles all public (non-authenticated) API requests.
 * URL pattern: /api/{endpoint}?slug={restaurant_slug}
 */

require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/Database.php';
require_once __DIR__ . '/../includes/helpers.php';

// Set CORS headers (needed if menu page is loaded from a different origin)
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// Only GET is allowed on public API
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    jsonError('Method not allowed', 405);
}

// Get endpoint: try query param first (for direct calls), then URL path
$endpoint = $_GET['endpoint'] ?? '';

if (empty($endpoint)) {
    $requestUri = $_SERVER['REQUEST_URI'] ?? '';
    $requestUri = preg_replace('/\?.*$/', '', $requestUri);
    $requestUri = trim($requestUri, '/');
    $endpoint = 'menu'; // default
    if (preg_match('#api/([a-zA-Z_]+)#', $requestUri, $matches)) {
        $endpoint = $matches[1];
    }
}

switch ($endpoint) {
    case 'menu':
        require_once __DIR__ . '/menu.php';
        $slug = $_GET['slug'] ?? '';
        if (empty($slug)) {
            jsonError('Restaurant slug is required');
        }
        $data = getMenuData(Database::getInstance(), $slug);
        if (!$data) {
            jsonError('Restaurant not found', 404);
        }
        jsonResponse($data);
        break;

    case 'restaurants':
        $db = Database::getInstance();
        $stmt = $db->query(
            "SELECT id, slug, name_ar, name_en, logo, address_ar, address_en, phone
             FROM restaurants
             WHERE is_active = 1
             ORDER BY sort_order ASC"
        );
        $restaurants = $stmt->fetchAll();
        jsonResponse(['restaurants' => $restaurants]);
        break;

    default:
        jsonError('Unknown endpoint', 404);
}
