<?php
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';

Auth::requireSuperAdmin();
$method = $_SERVER['REQUEST_METHOD'];
$db = Database::getInstance();

if ($method === 'GET') {
    $vipId = (int)($_GET['vip_item_id'] ?? 0);
    if (!$vipId) jsonError('vip_item_id required');
    $stmt = $db->prepare("SELECT * FROM vip_item_images WHERE vip_item_id=? ORDER BY sort_order ASC");
    $stmt->execute([$vipId]);
    jsonResponse(['images' => $stmt->fetchAll()]);
}

if ($method === 'POST') {
    Auth::validateCsrf();
    $body = getJsonBody();
    $vipId = (int)($body['vip_item_id'] ?? 0);
    if (!$vipId) jsonError('vip_item_id required');
    $sort = $db->prepare("SELECT MAX(sort_order)+1 FROM vip_item_images WHERE vip_item_id=?");
    $sort->execute([$vipId]);
    $so = $sort->fetchColumn() ?: 1;
    $db->prepare("INSERT INTO vip_item_images (vip_item_id,image_path,sort_order) VALUES (?,?,?)")
       ->execute([$vipId, $body['image_path'], $so]);
    $id = $db->lastInsertId();
    jsonResponse(['image' => $db->query("SELECT * FROM vip_item_images WHERE id=$id")->fetch()], 201);
}

if ($method === 'DELETE') {
    Auth::validateCsrf();
    $id = (int)($_GET['id'] ?? 0);
    if (!$id) jsonError('ID required');
    $db->prepare("DELETE FROM vip_item_images WHERE id=?")->execute([$id]);
    jsonResponse(['success' => true]);
}

jsonError('Method not allowed', 405);
