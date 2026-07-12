<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';

Auth::requireSuperAdmin();
$method = $_SERVER['REQUEST_METHOD'];
$db = Database::getInstance();

if ($method === 'GET') {
    $restId = (int)($_GET['restaurant_id'] ?? 0);
    if (!$restId) jsonError('restaurant_id required');
    $stmt = $db->prepare("SELECT * FROM vip_carousel_images WHERE restaurant_id=? ORDER BY sort_order ASC");
    $stmt->execute([$restId]);
    jsonResponse(['images' => $stmt->fetchAll()]);
}

if ($method === 'POST') {
    Auth::validateCsrf();
    $body = getJsonBody();
    $restId = (int)($body['restaurant_id'] ?? 0);
    if (!$restId) jsonError('restaurant_id required');
    $sort = $db->prepare("SELECT MAX(sort_order)+1 FROM vip_carousel_images WHERE restaurant_id=?");
    $sort->execute([$restId]);
    $so = $sort->fetchColumn() ?: 1;
    $db->prepare("INSERT INTO vip_carousel_images (restaurant_id,image_path,sort_order) VALUES (?,?,?)")
       ->execute([$restId, $body['image_path'], $so]);
    jsonResponse(['image' => $db->query("SELECT * FROM vip_carousel_images WHERE id=".$db->lastInsertId())->fetch()], 201);
}

if ($method === 'DELETE') {
    Auth::validateCsrf();
    $id = (int)($_GET['id'] ?? 0);
    if (!$id) jsonError('ID required');
    $db->prepare("DELETE FROM vip_carousel_images WHERE id=?")->execute([$id]);
    jsonResponse(['success' => true]);
}

jsonError('Method not allowed', 405);
