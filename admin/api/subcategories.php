<?php
/**
 * Subcategory CRUD — Standalone endpoint.
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
    if (!$categoryId) jsonError('category_id is required');
    $cat = $db->prepare("SELECT restaurant_id FROM categories WHERE id = ?");
    $cat->execute([$categoryId]);
    $c = $cat->fetch();
    if (!$c) jsonError('Category not found', 404);
    Auth::requireRestaurantAccess((int) $c['restaurant_id']);
    $stmt = $db->prepare("SELECT * FROM subcategories WHERE category_id = ? ORDER BY sort_order ASC");
    $stmt->execute([$categoryId]);
    jsonResponse(['subcategories' => $stmt->fetchAll()]);
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
    $db->prepare("INSERT INTO subcategories (category_id, name_ar, name_en, sort_order) VALUES (?, ?, ?, ?)")
       ->execute([$categoryId, $body['name_ar'] ?? '', $body['name_en'] ?? '', (int) ($body['sort_order'] ?? 0)]);
    $id = $db->lastInsertId();
    $sub = $db->prepare("SELECT * FROM subcategories WHERE id = ?");
    $sub->execute([$id]);
    jsonResponse(['subcategory' => $sub->fetch()], 201);
}

if ($method === 'PUT') {
    Auth::validateCsrf();
    $id = (int) ($_GET['id'] ?? 0);
    if (!$id) jsonError('ID is required');
    $sub = $db->prepare("SELECT s.id, c.restaurant_id FROM subcategories s JOIN categories c ON s.category_id = c.id WHERE s.id = ?");
    $sub->execute([$id]);
    $e = $sub->fetch();
    if (!$e) jsonError('Subcategory not found', 404);
    Auth::requireRestaurantAccess((int) $e['restaurant_id']);
    $body = getJsonBody();
    $fields = []; $params = [];
    foreach (['name_ar', 'name_en'] as $f) { if (isset($body[$f])) { $fields[] = "$f = ?"; $params[] = $body[$f]; } }
    foreach (['category_id', 'sort_order'] as $f) { if (isset($body[$f])) { $fields[] = "$f = ?"; $params[] = (int) $body[$f]; } }
    if (empty($fields)) jsonError('No fields to update');
    $params[] = $id;
    $db->prepare("UPDATE subcategories SET " . implode(', ', $fields) . " WHERE id = ?")->execute($params);
    $sub = $db->prepare("SELECT * FROM subcategories WHERE id = ?");
    $sub->execute([$id]);
    jsonResponse(['subcategory' => $sub->fetch()]);
}

if ($method === 'DELETE') {
    Auth::validateCsrf();
    $id = (int) ($_GET['id'] ?? 0);
    if (!$id) jsonError('ID is required');
    $sub = $db->prepare("SELECT s.id, c.restaurant_id FROM subcategories s JOIN categories c ON s.category_id = c.id WHERE s.id = ?");
    $sub->execute([$id]);
    $e = $sub->fetch();
    if (!$e) jsonError('Subcategory not found', 404);
    Auth::requireRestaurantAccess((int) $e['restaurant_id']);
    $db->prepare("DELETE FROM subcategories WHERE id = ?")->execute([$id]);
    jsonResponse(['success' => true]);
}

jsonError('Method not allowed', 405);
