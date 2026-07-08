<?php
/**
 * Configuration file for the Menu Platform.
 *
 * Database credentials and application constants.
 * On libyanspider shared hosting, update these values
 * to match the MySQL database created in cPanel.
 */

// Database configuration
define('DB_HOST', 'localhost');
define('DB_NAME', 'webichly_Restaurants');
define('DB_USER', 'webichly_Malek');  // Usually same as DB name on cPanel
define('DB_PASS', 'Mmrd113113d@113');
define('DB_CHARSET', 'utf8mb4');

// Application
define('APP_NAME', 'Lavina House');
define('APP_URL', 'https://restaurants.webich.ly');
define('UPLOAD_DIR', __DIR__ . '/../images');
define('STATIC_DIR', __DIR__ . '/../static');
define('MAX_UPLOAD_SIZE', 5 * 1024 * 1024);  // 5MB
define('ALLOWED_IMAGE_TYPES', ['image/jpeg', 'image/png', 'image/webp']);

// Session — must be set BEFORE session_start()
ini_set('session.cookie_path', '/');
ini_set('session.cookie_httponly', '1');
ini_set('session.cookie_samesite', 'Lax');
ini_set('session.use_strict_mode', '1');
define('SESSION_LIFETIME', 86400);  // 24 hours

// Currency
define('CURRENCY_AR', 'د.ل');
define('CURRENCY_EN', 'LYD');

// Error reporting (disable display in production)
error_reporting(E_ALL);
ini_set('display_errors', '0');
ini_set('log_errors', '1');

// Timezone
date_default_timezone_set('Africa/Tripoli');
