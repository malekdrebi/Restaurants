<?php
/**
 * Restaurant CRUD (super_admin only).
 */

function handleRestaurants(): void
{
    $method = $_SERVER['REQUEST_METHOD'];
    $db = Database::getInstance();

    // GET — list all (super_admin sees all, restaurant_admin sees only theirs)
    if ($method === 'GET') {
        $admin = Auth::user();

        if ($admin['role'] === 'super_admin') {
            $stmt = $db->query("SELECT * FROM restaurants ORDER BY sort_order ASC");
        } else {
            $stmt = $db->prepare("SELECT * FROM restaurants WHERE id = ?");
            $stmt->execute([$admin['restaurant_id']]);
        }
        jsonResponse(['restaurants' => $stmt->fetchAll()]);
    }

    // POST — create (super_admin only)
    if ($method === 'POST') {
        Auth::requireSuperAdmin();
        Auth::validateCsrf();

        $body = getJsonBody();
        $slug = slugify($body['name_en'] ?? $body['name_ar'] ?? 'restaurant');

        // Ensure unique slug
        $existing = $db->prepare("SELECT id FROM restaurants WHERE slug = ?");
        $existing->execute([$slug]);
        if ($existing->fetch()) {
            $slug .= '-' . time();
        }

        $stmt = $db->prepare(
            "INSERT INTO restaurants (slug, name_ar, name_en, address_ar, address_en, phone, sort_order)
             VALUES (?, ?, ?, ?, ?, ?, ?)"
        );
        $stmt->execute([
            $slug,
            $body['name_ar'] ?? '',
            $body['name_en'] ?? '',
            $body['address_ar'] ?? null,
            $body['address_en'] ?? null,
            $body['phone'] ?? null,
            (int) ($body['sort_order'] ?? 0),
        ]);

        $id = $db->lastInsertId();
        $restaurant = $db->prepare("SELECT * FROM restaurants WHERE id = ?");
        $restaurant->execute([$id]);
        jsonResponse(['restaurant' => $restaurant->fetch()], 201);
    }

    // PUT — update
    if ($method === 'PUT') {
        Auth::validateCsrf();
        $id = (int) ($_GET['id'] ?? 0);
        if (!$id) jsonError('ID is required');

        // Scope check: restaurant_admin can only update their own
        Auth::requireRestaurantAccess($id);

        $body = getJsonBody();
        $fields = [];
        $params = [];

        foreach (['name_ar', 'name_en', 'slug', 'address_ar', 'address_en', 'phone'] as $field) {
            if (isset($body[$field])) {
                $fields[] = "$field = ?";
                $params[] = $body[$field];
            }
        }
        foreach (['is_active', 'sort_order'] as $field) {
            if (isset($body[$field])) {
                $fields[] = "$field = ?";
                $params[] = (int) $body[$field];
            }
        }

        if (empty($fields)) jsonError('No fields to update');

        $params[] = $id;
        $stmt = $db->prepare("UPDATE restaurants SET " . implode(', ', $fields) . " WHERE id = ?");
        $stmt->execute($params);

        $restaurant = $db->prepare("SELECT * FROM restaurants WHERE id = ?");
        $restaurant->execute([$id]);
        jsonResponse(['restaurant' => $restaurant->fetch()]);
    }

    // DELETE — (super_admin only)
    if ($method === 'DELETE') {
        Auth::requireSuperAdmin();
        Auth::validateCsrf();

        $id = (int) ($_GET['id'] ?? 0);
        if (!$id) jsonError('ID is required');

        $stmt = $db->prepare("DELETE FROM restaurants WHERE id = ?");
        $stmt->execute([$id]);
        jsonResponse(['success' => true, 'message' => 'Restaurant deleted']);
    }

    jsonError('Method not allowed', 405);
}
