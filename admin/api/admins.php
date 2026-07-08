<?php
/**
 * Admin management (super_admin only).
 */

function handleAdmins(): void
{
    $method = $_SERVER['REQUEST_METHOD'];
    $db = Database::getInstance();

    // All admin management requires super_admin
    Auth::requireSuperAdmin();

    // GET — list all admins
    if ($method === 'GET') {
        $stmt = $db->query(
            "SELECT a.id, a.username, a.role, a.restaurant_id, a.created_at,
                    r.name_ar AS restaurant_name_ar, r.name_en AS restaurant_name_en
             FROM admins a
             LEFT JOIN restaurants r ON a.restaurant_id = r.id
             ORDER BY a.created_at DESC"
        );
        jsonResponse(['admins' => $stmt->fetchAll()]);
    }

    // POST — create admin
    if ($method === 'POST') {
        Auth::validateCsrf();
        $body = getJsonBody();
        $username = trim($body['username'] ?? '');
        $password = $body['password'] ?? '';
        $role = $body['role'] ?? 'restaurant_admin';
        $restaurantId = $body['restaurant_id'] ?? null;

        if (empty($username) || empty($password)) {
            jsonError('Username and password are required');
        }
        if (strlen($password) < 6) {
            jsonError('Password must be at least 6 characters');
        }
        if (!in_array($role, ['super_admin', 'restaurant_admin'])) {
            jsonError('Invalid role');
        }
        if ($role === 'restaurant_admin' && !$restaurantId) {
            jsonError('restaurant_id is required for restaurant_admin');
        }

        // Check username uniqueness
        $check = $db->prepare("SELECT id FROM admins WHERE username = ?");
        $check->execute([$username]);
        if ($check->fetch()) {
            jsonError('Username already taken');
        }

        $hash = Auth::hashPassword($password);

        $stmt = $db->prepare(
            "INSERT INTO admins (username, password_hash, role, restaurant_id) VALUES (?, ?, ?, ?)"
        );
        $stmt->execute([$username, $hash, $role, $role === 'super_admin' ? null : $restaurantId]);

        $id = $db->lastInsertId();
        $admin = $db->prepare(
            "SELECT a.id, a.username, a.role, a.restaurant_id, a.created_at
             FROM admins a WHERE a.id = ?"
        );
        $admin->execute([$id]);
        jsonResponse(['admin' => $admin->fetch()], 201);
    }

    // PUT — update admin
    if ($method === 'PUT') {
        Auth::validateCsrf();
        $id = (int) ($_GET['id'] ?? 0);
        if (!$id) jsonError('ID is required');

        $body = getJsonBody();
        $fields = [];
        $params = [];

        if (isset($body['username'])) {
            $check = $db->prepare("SELECT id FROM admins WHERE username = ? AND id != ?");
            $check->execute([trim($body['username']), $id]);
            if ($check->fetch()) jsonError('Username already taken');
            $fields[] = "username = ?";
            $params[] = trim($body['username']);
        }
        if (!empty($body['password'])) {
            if (strlen($body['password']) < 6) jsonError('Password must be at least 6 characters');
            $fields[] = "password_hash = ?";
            $params[] = Auth::hashPassword($body['password']);
        }
        if (isset($body['role'])) {
            if (!in_array($body['role'], ['super_admin', 'restaurant_admin'])) jsonError('Invalid role');
            $fields[] = "role = ?";
            $params[] = $body['role'];
        }
        if (array_key_exists('restaurant_id', $body)) {
            $fields[] = "restaurant_id = ?";
            $params[] = $body['restaurant_id'] ? (int) $body['restaurant_id'] : null;
        }

        if (empty($fields)) jsonError('No fields to update');
        $params[] = $id;
        $db->prepare("UPDATE admins SET " . implode(', ', $fields) . " WHERE id = ?")->execute($params);

        $admin = $db->prepare("SELECT a.id, a.username, a.role, a.restaurant_id, a.created_at FROM admins a WHERE a.id = ?");
        $admin->execute([$id]);
        jsonResponse(['admin' => $admin->fetch()]);
    }

    // DELETE
    if ($method === 'DELETE') {
        Auth::validateCsrf();
        $id = (int) ($_GET['id'] ?? 0);
        if (!$id) jsonError('ID is required');

        // Don't allow deleting yourself
        $currentAdmin = Auth::user();
        if ((int) $currentAdmin['id'] === $id) {
            jsonError('Cannot delete your own account');
        }

        $db->prepare("DELETE FROM admins WHERE id = ?")->execute([$id]);
        jsonResponse(['success' => true, 'message' => 'Admin deleted']);
    }

    jsonError('Method not allowed', 405);
}
