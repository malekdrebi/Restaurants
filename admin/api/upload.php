<?php
/**
 * Image upload — Standalone endpoint.
 */
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../includes/Auth.php';

Auth::require();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') jsonError('Method not allowed', 405);
Auth::validateCsrf();

$restaurantId = (int) ($_POST['restaurant_id'] ?? 0);
$restaurantSlug = $_POST['restaurant_slug'] ?? '';
if (!$restaurantId && !$restaurantSlug) jsonError('restaurant_id or restaurant_slug is required');

if (!$restaurantSlug) {
    $db = Database::getInstance();
    $stmt = $db->prepare("SELECT slug FROM restaurants WHERE id = ?");
    $stmt->execute([$restaurantId]);
    $r = $stmt->fetch();
    if (!$r) jsonError('Restaurant not found', 404);
    $restaurantSlug = $r['slug'];
}
Auth::requireRestaurantAccess($restaurantId);

if (!isset($_FILES['image'])) jsonError('No image file uploaded');
$file = $_FILES['image'];
if ($file['error'] !== UPLOAD_ERR_OK) jsonError('Upload error: ' . $file['error']);
if ($file['size'] > MAX_UPLOAD_SIZE) jsonError('File too large. Max ' . (MAX_UPLOAD_SIZE / 1024 / 1024) . 'MB');

$finfo = finfo_open(FILEINFO_MIME_TYPE);
$mime = finfo_file($finfo, $file['tmp_name']);
finfo_close($finfo);
if (!in_array($mime, ALLOWED_IMAGE_TYPES)) jsonError('Invalid file type. Allowed: JPEG, PNG, WebP');

$destDir = UPLOAD_DIR . '/' . $restaurantSlug . '/items';
ensureDir($destDir);
$ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
if (!in_array($ext, ['jpg', 'jpeg', 'png', 'webp'])) $ext = 'jpg';
$newName = 'item_' . time() . '_' . bin2hex(random_bytes(4)) . '.' . $ext;
$destPath = $destDir . '/' . $newName;

if (extension_loaded('gd')) {
    switch ($mime) {
        case 'image/jpeg': $src = imagecreatefromjpeg($file['tmp_name']); break;
        case 'image/png':  $src = imagecreatefrompng($file['tmp_name']); break;
        case 'image/webp': $src = imagecreatefromwebp($file['tmp_name']); break;
        default: $src = null;
    }
    if ($src) {
        $origW = imagesx($src); $origH = imagesy($src);
        $maxW = 1200; $maxH = 1200;
        if ($origW > $maxW || $origH > $maxH) {
            $ratio = min($maxW / $origW, $maxH / $origH);
            $newW = (int) round($origW * $ratio); $newH = (int) round($origH * $ratio);
            $dst = imagecreatetruecolor($newW, $newH);
            if ($mime === 'image/png') { imagealphablending($dst, false); imagesavealpha($dst, true); }
            imagecopyresampled($dst, $src, 0, 0, 0, 0, $newW, $newH, $origW, $origH);
            imagedestroy($src);
            $src = $dst;
        }
        switch ($ext) {
            case 'jpg': case 'jpeg': imagejpeg($src, $destPath, 85); break;
            case 'png': imagepng($src, $destPath, 7); break;
            case 'webp': imagewebp($src, $destPath, 85); break;
        }
        imagedestroy($src);
    } else {
        move_uploaded_file($file['tmp_name'], $destPath);
    }
} else {
    move_uploaded_file($file['tmp_name'], $destPath);
}

$relativePath = 'images/' . $restaurantSlug . '/items/' . $newName;
jsonResponse(['success' => true, 'path' => $relativePath, 'url' => '/' . $relativePath], 201);
