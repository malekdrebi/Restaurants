<?php
/**
 * Item CRUD — Standalone endpoint.
 */
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';

Auth::require();
$method = $_SERVER['REQUEST_METHOD'];
$db = Database::getInstance();

if ($method === 'GET') {
    $categoryId = (int) ($_GET['category_id'] ?? 0);
    $subcategoryId = $_GET['subcategory_id'] ?? null;
    if (!$categoryId) jsonError('category_id is required');
    $cat = $db->prepare("SELECT restaurant_id FROM categories WHERE id = ?");
    $cat->execute([$categoryId]);
    $c = $cat->fetch();
    if (!$c) jsonError('Category not found', 404);
    Auth::requireRestaurantAccess((int) $c['restaurant_id']);

    if ($subcategoryId !== null && $subcategoryId !== '') {
        $stmt = $db->prepare("SELECT * FROM items WHERE category_id = ? AND subcategory_id = ? ORDER BY sort_order ASC");
        $stmt->execute([$categoryId, (int) $subcategoryId]);
    } else {
        $stmt = $db->prepare("SELECT * FROM items WHERE category_id = ? AND subcategory_id IS NULL ORDER BY sort_order ASC");
        $stmt->execute([$categoryId]);
    }
    $items = $stmt->fetchAll();
    foreach ($items as &$item) {
        $v = $db->prepare("SELECT * FROM variants WHERE item_id = ? ORDER BY sort_order ASC");
        $v->execute([$item['id']]);
        $item['variants'] = $v->fetchAll();
    }
    jsonResponse(['items' => $items]);
}

if ($method === 'POST') {
    Auth::validateCsrf();
    $body = getJsonBody();
    $categoryId = (int) ($body['category_id'] ?? 0);
    if (!$categoryId) jsonError('category_id is required');
    $cat = $db->prepare("SELECT restaurant_id FROM categories WHERE id = ?");
    $cat->execute([$categoryId]);
    $c = $cat->fetch();
    if (!$c) jsonError('Category not found', 404);
    Auth::requireRestaurantAccess((int) $c['restaurant_id']);
    $subId = isset($body['subcategory_id']) && $body['subcategory_id'] !== '' ? (int) $body['subcategory_id'] : null;
    $db->prepare("INSERT INTO items (category_id, subcategory_id, name_ar, name_en, price, desc_ar, desc_en, image, spicy, recommended, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
       ->execute([$categoryId, $subId, $body['name_ar'] ?? '', $body['name_en'] ?? '', (float) ($body['price'] ?? 0), $body['desc_ar'] ?? '', $body['desc_en'] ?? '', $body['image'] ?? null, (int) ($body['spicy'] ?? 0), (int) ($body['recommended'] ?? 0), (int) ($body['sort_order'] ?? 0)]);
    $id = $db->lastInsertId();
    $item = $db->prepare("SELECT * FROM items WHERE id = ?");
    $item->execute([$id]);
    jsonResponse(['item' => $item->fetch()], 201);
}

if ($method === 'PUT') {
    Auth::validateCsrf();
    $id = (int) ($_GET['id'] ?? 0);
    if (!$id) jsonError('ID is required');
    $item = $db->prepare("SELECT i.id, c.restaurant_id FROM items i JOIN categories c ON i.category_id = c.id WHERE i.id = ?");
    $item->execute([$id]);
    $e = $item->fetch();
    if (!$e) jsonError('Item not found', 404);
    Auth::requireRestaurantAccess((int) $e['restaurant_id']);
    $body = getJsonBody();
    $fields = []; $params = [];
    foreach (['name_ar', 'name_en', 'desc_ar', 'desc_en', 'image'] as $f) { if (array_key_exists($f, $body)) { $fields[] = "$f = ?"; $params[] = $body[$f]; } }
    if (array_key_exists('price', $body)) { $fields[] = "price = ?"; $params[] = (float) $body['price']; }
    foreach (['category_id', 'subcategory_id', 'spicy', 'recommended', 'sort_order'] as $f) {
        if (array_key_exists($f, $body)) { $fields[] = "$f = ?"; $params[] = ($body[$f] === '' || $body[$f] === null) ? null : (int) $body[$f]; }
    }
    if (empty($fields)) jsonError('No fields to update');
    $params[] = $id;
    $db->prepare("UPDATE items SET " . implode(', ', $fields) . " WHERE id = ?")->execute($params);
    $item = $db->prepare("SELECT * FROM items WHERE id = ?");
    $item->execute([$id]);
    jsonResponse(['item' => $item->fetch()]);
}

if ($method === 'DELETE') {
    Auth::validateCsrf();
    $id = (int) ($_GET['id'] ?? 0);
    if (!$id) jsonError('ID is required');
    $item = $db->prepare("SELECT i.id, c.restaurant_id FROM items i JOIN categories c ON i.category_id = c.id WHERE i.id = ?");
    $item->execute([$id]);
    $e = $item->fetch();
    if (!$e) jsonError('Item not found', 404);
    Auth::requireRestaurantAccess((int) $e['restaurant_id']);
    $db->prepare("DELETE FROM items WHERE id = ?")->execute([$id]);
    jsonResponse(['success' => true]);
}

jsonError('Method not allowed', 405);
