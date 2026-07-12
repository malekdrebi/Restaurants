<?php
/**
 * Restaurant CRUD — Standalone endpoint (super_admin only for POST/PUT/DELETE).
 */
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';

$admin = Auth::require();
$method = $_SERVER['REQUEST_METHOD'];
$db = Database::getInstance();

if ($method === 'GET') {
    if ($admin['role'] === 'super_admin') {
        $restaurants = $db->query("SELECT * FROM restaurants ORDER BY sort_order ASC")->fetchAll();
    } else {
        $stmt = $db->prepare("SELECT * FROM restaurants WHERE id = ?");
        $stmt->execute([$admin['restaurant_id']]);
        $restaurants = $stmt->fetchAll();
    }
    jsonResponse(['restaurants' => $restaurants]);
}

if ($method === 'POST') {
    Auth::requireSuperAdmin();
    Auth::validateCsrf();
    $body = getJsonBody();
    $slug = slugify($body['slug'] ?: ($body['name_en'] ?? 'restaurant'));
    $check = $db->prepare("SELECT id FROM restaurants WHERE slug = ?");
    $check->execute([$slug]);
    if ($check->fetch()) $slug .= '-' . time();

    $db->prepare("INSERT INTO restaurants (slug, name_ar, name_en, address_ar, address_en, phone, sort_order) VALUES (?,?,?,?,?,?,?)")
       ->execute([$slug, $body['name_ar']??'', $body['name_en']??'', $body['address_ar']??null, $body['address_en']??null, $body['phone']??null, (int)($body['sort_order']??0)]);
    $id = $db->lastInsertId();
    $r = $db->prepare("SELECT * FROM restaurants WHERE id = ?");
    $r->execute([$id]);
    jsonResponse(['restaurant' => $r->fetch()], 201);
}

if ($method === 'PUT') {
    Auth::requireSuperAdmin();
    Auth::validateCsrf();
    $id = (int)($_GET['id']??0);
    if (!$id) jsonError('ID required');
    $body = getJsonBody();
    $fields=[]; $params=[];
    foreach(['name_ar','name_en','slug','address_ar','address_en','phone','maps_url','logo','bg_image','vip_hero_bg','primary_color','show_vip','show_gallery','show_tutorial','show_cart','show_parallax','show_hub','show_vip_prices'] as $f) {
        if(isset($body[$f])){$fields[]="$f=?";$params[]=$body[$f];}
    }
    foreach(['is_active','sort_order','show_vip_prices'] as $f) {
        if(isset($body[$f])){$fields[]="$f=?";$params[]=(int)$body[$f];}
    }
    if(empty($fields)) jsonError('No fields');
    $params[]=$id;
    $db->prepare("UPDATE restaurants SET ".implode(', ',$fields)." WHERE id=?")->execute($params);
    $r = $db->prepare("SELECT * FROM restaurants WHERE id=?");
    $r->execute([$id]);
    jsonResponse(['restaurant' => $r->fetch()]);
}

if ($method === 'DELETE') {
    Auth::requireSuperAdmin();
    Auth::validateCsrf();
    $id = (int)($_GET['id']??0);
    if (!$id) jsonError('ID required');
    $db->prepare("DELETE FROM restaurants WHERE id=?")->execute([$id]);
    jsonResponse(['success' => true]);
}

jsonError('Method not allowed', 405);
