<?php
/**
 * Emergency password reset.
 * DELETE THIS FILE AFTER USE.
 */

require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/Database.php';

$db = Database::getInstance();

// Reset admin password
$newPassword = 'admin123';
$hash = password_hash($newPassword, PASSWORD_BCRYPT);

$stmt = $db->prepare("UPDATE admins SET password_hash = ? WHERE username = 'admin'");
$stmt->execute([$hash]);

// Also make sure the admin is super_admin
$db->prepare("UPDATE admins SET role = 'super_admin', restaurant_id = NULL WHERE username = 'admin'")->execute();

echo "Password reset!<br>";
echo "Username: <b>admin</b><br>";
echo "New password: <b>{$newPassword}</b><br>";
echo "<br><a href='index.html'>Go to login</a><br>";
echo "<br><b style='color:red'>DELETE THIS FILE (admin/reset.php) AFTER USE!</b>";
