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
    $stmt = $db->prepare("SELECT * FROM gallery_images WHERE restaurant_id=? ORDER BY sort_order ASC");
    $stmt->execute([$restId]);
    jsonResponse(['images' => $stmt->fetchAll()]);
}

if ($method === 'POST') {
    Auth::validateCsrf();
    $restId = (int)($_POST['restaurant_id'] ?? 0);
    if (!$restId) jsonError('restaurant_id required');
    if (empty($_FILES['image'])) jsonError('No image');
    $file = $_FILES['image'];
    if ($file['error'] !== UPLOAD_ERR_OK) jsonError('Upload error');

    $r = $db->prepare("SELECT slug FROM restaurants WHERE id=?");
    $r->execute([$restId]); $rest = $r->fetch();
    if (!$rest) jsonError('Restaurant not found');

    $destDir = UPLOAD_DIR . '/' . $rest['slug'] . '/gallery';
    ensureDir($destDir);
    $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    $name = 'gallery_' . time() . '_' . bin2hex(random_bytes(4)) . '.' . $ext;
    $dest = $destDir . '/' . $name;
    move_uploaded_file($file['tmp_name'], $dest);
    $path = 'images/' . $rest['slug'] . '/gallery/' . $name;

    $sort = $db->prepare("SELECT MAX(sort_order)+1 FROM gallery_images WHERE restaurant_id=?");
    $sort->execute([$restId]);
    $so = $sort->fetchColumn() ?: 1;

    $db->prepare("INSERT INTO gallery_images (restaurant_id,image_path,sort_order) VALUES (?,?,?)")->execute([$restId,$path,$so]);
    $id = $db->lastInsertId();
    $img = $db->prepare("SELECT * FROM gallery_images WHERE id=?");
    $img->execute([$id]);
    jsonResponse(['image' => $img->fetch()], 201);
}

if ($method === 'DELETE') {
    Auth::validateCsrf();
    $id = (int)($_GET['id'] ?? 0);
    if (!$id) jsonError('ID required');
    $db->prepare("DELETE FROM gallery_images WHERE id=?")->execute([$id]);
    jsonResponse(['success' => true]);
}

jsonError('Method not allowed', 405);
