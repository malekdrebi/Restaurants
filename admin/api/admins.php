<?php
/**
 * Admin management — Standalone endpoint (super_admin only).
 */
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';

Auth::requireSuperAdmin();
$method = $_SERVER['REQUEST_METHOD'];
$db = Database::getInstance();

if ($method === 'GET') {
    $admins = $db->query("SELECT a.id,a.username,a.role,a.restaurant_id,a.created_at,r.name_en as restaurant_name_en,r.name_ar as restaurant_name_ar FROM admins a LEFT JOIN restaurants r ON a.restaurant_id=r.id ORDER BY a.created_at DESC")->fetchAll();
    jsonResponse(['admins' => $admins]);
}

if ($method === 'POST') {
    Auth::validateCsrf();
    $body = getJsonBody();
    $username = trim($body['username']??'');
    $password = $body['password']??'';
    $role = $body['role']??'restaurant_admin';
    $restId = $body['restaurant_id']??null;
    if (empty($username)||empty($password)) jsonError('Username and password required');
    if (strlen($password)<6) jsonError('Password must be 6+ chars');
    if (!in_array($role,['super_admin','restaurant_admin'])) jsonError('Invalid role');
    $check = $db->prepare("SELECT id FROM admins WHERE username=?");
    $check->execute([$username]);
    if($check->fetch()) jsonError('Username taken');
    $db->prepare("INSERT INTO admins (username,password_hash,role,restaurant_id) VALUES (?,?,?,?)")
       ->execute([$username, Auth::hashPassword($password), $role, $role==='super_admin'?null:$restId]);
    $id = $db->lastInsertId();
    $a = $db->prepare("SELECT id,username,role,restaurant_id,created_at FROM admins WHERE id=?");
    $a->execute([$id]);
    jsonResponse(['admin' => $a->fetch()],201);
}

if ($method === 'DELETE') {
    Auth::validateCsrf();
    $id = (int)($_GET['id']??0);
    if(!$id) jsonError('ID required');
    if((int)Auth::user()['id']===$id) jsonError('Cannot delete yourself');
    $db->prepare("DELETE FROM admins WHERE id=?")->execute([$id]);
    jsonResponse(['success'=>true]);
}

jsonError('Method not allowed',405);
