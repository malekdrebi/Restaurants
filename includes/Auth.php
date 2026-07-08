<?php
/**
 * Authentication helper class.
 *
 * Handles login, logout, session management, and role-based access control.
 */
class Auth
{
    /**
     * Attempt login with username and password.
     * Returns admin array on success, null on failure.
     */
    public static function login(string $username, string $password): ?array
    {
        $db = Database::getInstance();

        $stmt = $db->prepare(
            "SELECT a.id, a.username, a.password_hash, a.role, a.restaurant_id,
                    r.slug AS restaurant_slug, r.name_ar AS restaurant_name_ar, r.name_en AS restaurant_name_en
             FROM admins a
             LEFT JOIN restaurants r ON a.restaurant_id = r.id
             WHERE a.username = ?"
        );
        $stmt->execute([$username]);
        $admin = $stmt->fetch();

        if (!$admin) {
            return null;
        }

        if (!password_verify($password, $admin['password_hash'])) {
            return null;
        }

        // Remove hash from session data
        unset($admin['password_hash']);

        // Store in session
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        session_regenerate_id(true);
        $_SESSION['admin'] = $admin;
        $_SESSION['admin_logged_in_at'] = time();

        return $admin;
    }

    /**
     * Log out the current admin.
     */
    public static function logout(): void
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        $_SESSION = [];
        if (ini_get('session.use_cookies')) {
            $params = session_get_cookie_params();
            setcookie(
                session_name(),
                '',
                time() - 42000,
                $params['path'],
                $params['domain'],
                $params['secure'],
                $params['httponly']
            );
        }
        session_destroy();
    }

    /**
     * Get the currently authenticated admin, or null.
     */
    public static function user(): ?array
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        return $_SESSION['admin'] ?? null;
    }

    /**
     * Check if an admin is authenticated. Send 401 if not.
     */
    public static function require(): array
    {
        $admin = self::user();
        if (!$admin) {
            http_response_code(401);
            header('Content-Type: application/json; charset=utf-8');
            echo json_encode(['error' => 'Authentication required']);
            exit;
        }
        return $admin;
    }

    /**
     * Require super admin role. Send 403 if not.
     */
    public static function requireSuperAdmin(): array
    {
        $admin = self::require();
        if ($admin['role'] !== 'super_admin') {
            http_response_code(403);
            header('Content-Type: application/json; charset=utf-8');
            echo json_encode(['error' => 'Super admin access required']);
            exit;
        }
        return $admin;
    }

    /**
     * Check if the current admin can access a specific restaurant.
     */
    public static function canAccessRestaurant(int $restaurantId): bool
    {
        $admin = self::user();
        if (!$admin) return false;
        if ($admin['role'] === 'super_admin') return true;
        return (int) $admin['restaurant_id'] === $restaurantId;
    }

    /**
     * Require access to a specific restaurant. Send 403 if denied.
     */
    public static function requireRestaurantAccess(int $restaurantId): array
    {
        $admin = self::require();
        if (!self::canAccessRestaurant($restaurantId)) {
            http_response_code(403);
            header('Content-Type: application/json; charset=utf-8');
            echo json_encode(['error' => 'Access to this restaurant denied']);
            exit;
        }
        return $admin;
    }

    /**
     * Get the restaurant ID that the current admin is scoped to.
     * Returns null for super admins (meaning all restaurants).
     */
    public static function scopedRestaurantId(): ?int
    {
        $admin = self::user();
        if (!$admin) return null;
        if ($admin['role'] === 'super_admin') return null;
        return (int) $admin['restaurant_id'];
    }

    /**
     * CSRF token management.
     */
    public static function csrfToken(): string
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        if (empty($_SESSION['csrf_token'])) {
            $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
        }
        return $_SESSION['csrf_token'];
    }

    public static function validateCsrf(): void
    {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
        $token = $_SERVER['HTTP_X_CSRF_TOKEN'] ?? $_POST['csrf_token'] ?? null;
        if (!$token || !isset($_SESSION['csrf_token']) || !hash_equals($_SESSION['csrf_token'], $token)) {
            http_response_code(403);
            header('Content-Type: application/json; charset=utf-8');
            echo json_encode(['error' => 'Invalid CSRF token']);
            exit;
        }
    }

    /**
     * Hash a password using bcrypt.
     */
    public static function hashPassword(string $password): string
    {
        return password_hash($password, PASSWORD_BCRYPT);
    }

    /**
     * Verify a password against a hash.
     */
    public static function verifyPassword(string $password, string $hash): bool
    {
        return password_verify($password, $hash);
    }
}
