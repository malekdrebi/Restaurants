<?php
/**
 * Image upload handler.
 */

function handleUpload(): void
{
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        jsonError('Method not allowed', 405);
    }

    Auth::validateCsrf();

    $restaurantId = (int) ($_POST['restaurant_id'] ?? 0);
    $restaurantSlug = $_POST['restaurant_slug'] ?? '';

    if (!$restaurantId && !$restaurantSlug) {
        jsonError('restaurant_id or restaurant_slug is required');
    }

    // Get restaurant slug if only ID provided
    if (!$restaurantSlug) {
        $db = Database::getInstance();
        $stmt = $db->prepare("SELECT slug FROM restaurants WHERE id = ?");
        $stmt->execute([$restaurantId]);
        $r = $stmt->fetch();
        if (!$r) jsonError('Restaurant not found', 404);
        $restaurantSlug = $r['slug'];
    }

    Auth::requireRestaurantAccess($restaurantId);

    if (!isset($_FILES['image'])) {
        jsonError('No image file uploaded');
    }

    $file = $_FILES['image'];

    if ($file['error'] !== UPLOAD_ERR_OK) {
        jsonError('Upload error: ' . $file['error']);
    }

    if ($file['size'] > MAX_UPLOAD_SIZE) {
        jsonError('File too large. Maximum size is ' . (MAX_UPLOAD_SIZE / 1024 / 1024) . 'MB');
    }

    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mime = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);

    if (!in_array($mime, ALLOWED_IMAGE_TYPES)) {
        jsonError('Invalid file type: ' . $mime . '. Allowed: JPEG, PNG, WebP');
    }

    // Create destination
    $destDir = UPLOAD_DIR . '/' . $restaurantSlug . '/items';
    ensureDir($destDir);

    $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    if (!in_array($ext, ['jpg', 'jpeg', 'png', 'webp'])) {
        $ext = 'jpg';
    }

    $newName = 'item_' . time() . '_' . bin2hex(random_bytes(4)) . '.' . $ext;
    $destPath = $destDir . '/' . $newName;

    // Resize image if needed (GD library)
    $resized = resizeImage($file['tmp_name'], $mime, 1200, 1200);

    if ($resized) {
        switch ($ext) {
            case 'jpg':
            case 'jpeg':
                imagejpeg($resized, $destPath, 85);
                break;
            case 'png':
                imagepng($resized, $destPath, 7);
                break;
            case 'webp':
                imagewebp($resized, $destPath, 85);
                break;
        }
        imagedestroy($resized);
    } else {
        // GD not available or unsupported type — move as-is
        move_uploaded_file($file['tmp_name'], $destPath);
    }

    $relativePath = 'images/' . $restaurantSlug . '/items/' . $newName;

    jsonResponse([
        'success' => true,
        'path' => $relativePath,
        'url' => '/' . $relativePath,
    ], 201);
}

/**
 * Resize an image to fit within max dimensions.
 * Returns GD resource or null if GD not available.
 */
function resizeImage(string $srcPath, string $mime, int $maxW, int $maxH)
{
    if (!extension_loaded('gd')) {
        return null;
    }

    switch ($mime) {
        case 'image/jpeg':
            $src = imagecreatefromjpeg($srcPath);
            break;
        case 'image/png':
            $src = imagecreatefrompng($srcPath);
            break;
        case 'image/webp':
            $src = imagecreatefromwebp($srcPath);
            break;
        default:
            return null;
    }

    if (!$src) return null;

    $origW = imagesx($src);
    $origH = imagesy($src);

    // Don't upscale
    if ($origW <= $maxW && $origH <= $maxH) {
        return $src;
    }

    $ratio = min($maxW / $origW, $maxH / $origH);
    $newW = (int) round($origW * $ratio);
    $newH = (int) round($origH * $ratio);

    $dst = imagecreatetruecolor($newW, $newH);

    // Preserve transparency for PNG
    if ($mime === 'image/png') {
        imagealphablending($dst, false);
        imagesavealpha($dst, true);
    }

    imagecopyresampled($dst, $src, 0, 0, 0, 0, $newW, $newH, $origW, $origH);
    imagedestroy($src);

    return $dst;
}
