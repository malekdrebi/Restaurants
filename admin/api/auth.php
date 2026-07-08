<?php
/**
 * Auth endpoints: login, logout, session check.
 */

function handleAuth(): void
{
    $action = $_GET['action'] ?? '';

    switch ($action) {
        case 'login':
            if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
                jsonError('Method not allowed', 405);
            }
            $body = getJsonBody();
            $username = trim($body['username'] ?? '');
            $password = $body['password'] ?? '';

            if (empty($username) || empty($password)) {
                jsonError('Username and password are required');
            }

            // Rate limiting: max 5 attempts per minute per IP
            $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
            $attemptKey = 'login_attempts_' . $ip;
            if (session_status() === PHP_SESSION_NONE) session_start();
            $attempts = $_SESSION[$attemptKey] ?? ['count' => 0, 'first_at' => time()];

            if (time() - $attempts['first_at'] > 60) {
                $attempts = ['count' => 0, 'first_at' => time()];
            }

            if ($attempts['count'] >= 5) {
                jsonError('Too many login attempts. Please wait a minute.', 429);
            }

            $admin = Auth::login($username, $password);

            if ($admin) {
                unset($_SESSION[$attemptKey]);
                jsonResponse([
                    'success' => true,
                    'admin' => [
                        'id' => $admin['id'],
                        'username' => $admin['username'],
                        'role' => $admin['role'],
                        'restaurant_id' => $admin['restaurant_id'],
                        'restaurant_slug' => $admin['restaurant_slug'] ?? null,
                        'restaurant_name_ar' => $admin['restaurant_name_ar'] ?? null,
                        'restaurant_name_en' => $admin['restaurant_name_en'] ?? null,
                    ],
                    'csrf_token' => Auth::csrfToken(),
                ]);
            } else {
                $attempts['count']++;
                $_SESSION[$attemptKey] = $attempts;
                jsonError('Invalid username or password', 401);
            }
            break;

        case 'logout':
            Auth::logout();
            jsonResponse(['success' => true, 'message' => 'Logged out']);
            break;

        case 'me':
            $admin = Auth::user();
            jsonResponse([
                'admin' => [
                    'id' => $admin['id'],
                    'username' => $admin['username'],
                    'role' => $admin['role'],
                    'restaurant_id' => $admin['restaurant_id'],
                    'restaurant_slug' => $admin['restaurant_slug'] ?? null,
                    'restaurant_name_ar' => $admin['restaurant_name_ar'] ?? null,
                    'restaurant_name_en' => $admin['restaurant_name_en'] ?? null,
                ],
                'csrf_token' => Auth::csrfToken(),
            ]);
            break;

        default:
            jsonError('Unknown auth action', 404);
    }
}
