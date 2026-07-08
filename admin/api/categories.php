<?php
/**
 * Category CRUD — Standalone endpoint.
 * URL: /admin/api/categories.php?restaurant_id=X
 */
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';

Auth::require();

$method = $_SERVER['REQUEST_METHOD'];
$db = Database::getInstance();

// GET — list categories for a restaurant
if ($method === 'GET') {
    $restaurantId = (int) ($_GET['restaurant_id'] ?? 0);
    if (!$restaurantId) jsonError('restaurant_id is required');
    Auth::requireRestaurantAccess($restaurantId);
    $stmt = $db->prepare("SELECT * FROM categories WHERE restaurant_id = ? ORDER BY sort_order ASC");
    $stmt->execute([$restaurantId]);
    jsonResponse(['categories' => $stmt->fetchAll()]);
}

// POST — create
if ($method === 'POST') {
    Auth::validateCsrf();
    $body = getJsonBody();
    $restaurantId = (int) ($body['restaurant_id'] ?? 0);
    if (!$restaurantId) jsonError('restaurant_id is required');
    Auth::requireRestaurantAccess($restaurantId);

    $stmt = $db->prepare(
        "INSERT INTO categories (restaurant_id, name_ar, name_en, image, is_featured, featured_type, sort_order)
         VALUES (?, ?, ?, ?, ?, ?, ?)"
    );
    $stmt->execute([
        $restaurantId,
        $body['name_ar'] ?? '',
        $body['name_en'] ?? '',
        $body['image'] ?? null,
        (int) ($body['is_featured'] ?? 0),
        $body['featured_type'] ?? null,
        (int) ($body['sort_order'] ?? 0),
    ]);

    $id = $db->lastInsertId();
    $cat = $db->prepare("SELECT * FROM categories WHERE id = ?");
    $cat->execute([$id]);
    jsonResponse(['category' => $cat->fetch()], 201);
}

// PUT — update
if ($method === 'PUT') {
    Auth::validateCsrf();
    $id = (int) ($_GET['id'] ?? 0);
    if (!$id) jsonError('ID is required');

    $cat = $db->prepare("SELECT restaurant_id FROM categories WHERE id = ?");
    $cat->execute([$id]);
    $existing = $cat->fetch();
    if (!$existing) jsonError('Category not found', 404);
    Auth::requireRestaurantAccess((int) $existing['restaurant_id']);

    $body = getJsonBody();
    $fields = [];
    $params = [];
    foreach (['name_ar', 'name_en', 'image', 'featured_type'] as $f) {
        if (isset($body[$f])) { $fields[] = "$f = ?"; $params[] = $body[$f]; }
    }
    foreach (['is_featured', 'sort_order'] as $f) {
        if (isset($body[$f])) { $fields[] = "$f = ?"; $params[] = (int) $body[$f]; }
    }
    if (empty($fields)) jsonError('No fields to update');
    $params[] = $id;
    $db->prepare("UPDATE categories SET " . implode(', ', $fields) . " WHERE id = ?")->execute($params);

    $cat = $db->prepare("SELECT * FROM categories WHERE id = ?");
    $cat->execute([$id]);
    jsonResponse(['category' => $cat->fetch()]);
}

// DELETE
if ($method === 'DELETE') {
    Auth::validateCsrf();
    $id = (int) ($_GET['id'] ?? 0);
    if (!$id) jsonError('ID is required');

    $cat = $db->prepare("SELECT restaurant_id FROM categories WHERE id = ?");
    $cat->execute([$id]);
    $existing = $cat->fetch();
    if (!$existing) jsonError('Category not found', 404);
    Auth::requireRestaurantAccess((int) $existing['restaurant_id']);

    $db->prepare("DELETE FROM categories WHERE id = ?")->execute([$id]);
    jsonResponse(['success' => true]);
}

jsonError('Method not allowed', 405);
