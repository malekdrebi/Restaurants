<?php
/**
 * Variant CRUD — Standalone endpoint.
 */
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';

Auth::require();
$method = $_SERVER['REQUEST_METHOD'];
$db = Database::getInstance();

if ($method === 'GET') {
    $itemId = (int) ($_GET['item_id'] ?? 0);
    if (!$itemId) jsonError('item_id is required');
    $item = $db->prepare("SELECT i.id, c.restaurant_id FROM items i JOIN categories c ON i.category_id = c.id WHERE i.id = ?");
    $item->execute([$itemId]);
    $e = $item->fetch();
    if (!$e) jsonError('Item not found', 404);
    Auth::requireRestaurantAccess((int) $e['restaurant_id']);
    $stmt = $db->prepare("SELECT * FROM variants WHERE item_id = ? ORDER BY sort_order ASC");
    $stmt->execute([$itemId]);
    jsonResponse(['variants' => $stmt->fetchAll()]);
}

if ($method === 'POST') {
    Auth::validateCsrf();
    $body = getJsonBody();
    $itemId = (int) ($body['item_id'] ?? 0);
    if (!$itemId) jsonError('item_id is required');
    $item = $db->prepare("SELECT i.id, c.restaurant_id FROM items i JOIN categories c ON i.category_id = c.id WHERE i.id = ?");
    $item->execute([$itemId]);
    $e = $item->fetch();
    if (!$e) jsonError('Item not found', 404);
    Auth::requireRestaurantAccess((int) $e['restaurant_id']);
    $db->prepare("INSERT INTO variants (item_id, name_ar, name_en, price, desc_ar, desc_en, image, sort_order) VALUES (?, ?, ?, ?, ?, ?, ?, ?)")
       ->execute([$itemId, $body['name_ar'] ?? '', $body['name_en'] ?? '', isset($body['price']) ? (float) $body['price'] : null, $body['desc_ar'] ?? '', $body['desc_en'] ?? '', $body['image'] ?? null, (int) ($body['sort_order'] ?? 0)]);
    $id = $db->lastInsertId();
    $v = $db->prepare("SELECT * FROM variants WHERE id = ?");
    $v->execute([$id]);
    jsonResponse(['variant' => $v->fetch()], 201);
}

if ($method === 'PUT') {
    Auth::validateCsrf();
    $id = (int) ($_GET['id'] ?? 0);
    if (!$id) jsonError('ID is required');
    $v = $db->prepare("SELECT v.id, c.restaurant_id FROM variants v JOIN items i ON v.item_id = i.id JOIN categories c ON i.category_id = c.id WHERE v.id = ?");
    $v->execute([$id]);
    $e = $v->fetch();
    if (!$e) jsonError('Variant not found', 404);
    Auth::requireRestaurantAccess((int) $e['restaurant_id']);
    $body = getJsonBody();
    $fields = []; $params = [];
    foreach (['name_ar', 'name_en', 'desc_ar', 'desc_en', 'image'] as $f) { if (array_key_exists($f, $body)) { $fields[] = "$f = ?"; $params[] = $body[$f]; } }
    foreach (['price', 'sort_order'] as $f) { if (array_key_exists($f, $body)) { $fields[] = "$f = ?"; $params[] = ($body[$f] === '' || $body[$f] === null) ? null : (float) $body[$f]; } }
    if (empty($fields)) jsonError('No fields to update');
    $params[] = $id;
    $db->prepare("UPDATE variants SET " . implode(', ', $fields) . " WHERE id = ?")->execute($params);
    $v = $db->prepare("SELECT * FROM variants WHERE id = ?");
    $v->execute([$id]);
    jsonResponse(['variant' => $v->fetch()]);
}

if ($method === 'DELETE') {
    Auth::validateCsrf();
    $id = (int) ($_GET['id'] ?? 0);
    if (!$id) jsonError('ID is required');
    $v = $db->prepare("SELECT v.id, c.restaurant_id FROM variants v JOIN items i ON v.item_id = i.id JOIN categories c ON i.category_id = c.id WHERE v.id = ?");
    $v->execute([$id]);
    $e = $v->fetch();
    if (!$e) jsonError('Variant not found', 404);
    Auth::requireRestaurantAccess((int) $e['restaurant_id']);
    $db->prepare("DELETE FROM variants WHERE id = ?")->execute([$id]);
    jsonResponse(['success' => true]);
}

jsonError('Method not allowed', 405);
