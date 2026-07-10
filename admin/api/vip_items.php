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
    $stmt = $db->prepare("SELECT * FROM vip_items WHERE restaurant_id=? ORDER BY sort_order ASC");
    $stmt->execute([$restId]);
    jsonResponse(['items' => $stmt->fetchAll()]);
}

if ($method === 'POST') {
    Auth::validateCsrf();
    $body = getJsonBody();
    $restId = (int)($body['restaurant_id'] ?? 0);
    if (!$restId) jsonError('restaurant_id required');
    $sort = $db->prepare("SELECT MAX(sort_order)+1 FROM vip_items WHERE restaurant_id=?");
    $sort->execute([$restId]);
    $so = $sort->fetchColumn() ?: 1;
    $db->prepare("INSERT INTO vip_items (restaurant_id,title_ar,title_en,desc_ar,desc_en,price,image_path,sort_order) VALUES (?,?,?,?,?,?,?,?)")
       ->execute([$restId, $body['title_ar']??'', $body['title_en']??'', $body['desc_ar']??'', $body['desc_en']??'', $body['price']??'', $body['image_path']??null, $so]);
    $id = $db->lastInsertId();
    $item = $db->prepare("SELECT * FROM vip_items WHERE id=?");
    $item->execute([$id]);
    jsonResponse(['item' => $item->fetch()], 201);
}

if ($method === 'PUT') {
    Auth::validateCsrf();
    $id = (int)($_GET['id'] ?? 0);
    if (!$id) jsonError('ID required');
    $body = getJsonBody();
    $fields=[]; $params=[];
    foreach(['title_ar','title_en','desc_ar','desc_en','price','image_path','sort_order'] as $f) {
        if(isset($body[$f])){$fields[]="$f=?";$params[]=$body[$f];}
    }
    if(empty($fields)) jsonError('No fields');
    $params[]=$id;
    $db->prepare("UPDATE vip_items SET ".implode(', ',$fields)." WHERE id=?")->execute($params);
    $item = $db->prepare("SELECT * FROM vip_items WHERE id=?");
    $item->execute([$id]);
    jsonResponse(['item' => $item->fetch()]);
}

if ($method === 'DELETE') {
    Auth::validateCsrf();
    $id = (int)($_GET['id'] ?? 0);
    if (!$id) jsonError('ID required');
    $db->prepare("DELETE FROM vip_items WHERE id=?")->execute([$id]);
    jsonResponse(['success' => true]);
}

jsonError('Method not allowed', 405);
