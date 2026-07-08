<?php
/**
 * Category CRUD.
 */

function handleCategories(): void
{
    $method = $_SERVER['REQUEST_METHOD'];
    $db = Database::getInstance();
    $admin = Auth::user();

    // GET — list categories for a restaurant
    if ($method === 'GET') {
        $restaurantId = (int) ($_GET['restaurant_id'] ?? 0);
        if (!$restaurantId) jsonError('restaurant_id is required');

        Auth::requireRestaurantAccess($restaurantId);

        $stmt = $db->prepare(
            "SELECT * FROM categories WHERE restaurant_id = ? ORDER BY sort_order ASC"
        );
        $stmt->execute([$restaurantId]);
        jsonResponse(['categories' => $stmt->fetchAll()]);
    }

    // POST — create
    if ($method === 'POST') {
        Auth::validateCsrf();
        $body = getJsonBody();
        $restaurantId = (int) ($body['restaurant_id'] ?? 0);
        if (!$restaurantId) jsonError('restaurant_id is required');

        Auth::requireRestaurantAccess($restaurantId);

        $stmt = $db->prepare(
            "INSERT INTO categories (restaurant_id, name_ar, name_en, image, is_featured, featured_type, sort_order)
             VALUES (?, ?, ?, ?, ?, ?, ?)"
        );
        $stmt->execute([
            $restaurantId,
            $body['name_ar'] ?? '',
            $body['name_en'] ?? '',
            $body['image'] ?? null,
            (int) ($body['is_featured'] ?? 0),
            $body['featured_type'] ?? null,
            (int) ($body['sort_order'] ?? 0),
        ]);

        $id = $db->lastInsertId();
        $cat = $db->prepare("SELECT * FROM categories WHERE id = ?");
        $cat->execute([$id]);
        jsonResponse(['category' => $cat->fetch()], 201);
    }

    // PUT — update
    if ($method === 'PUT') {
        Auth::validateCsrf();
        $id = (int) ($_GET['id'] ?? 0);
        if (!$id) jsonError('ID is required');

        // Verify ownership via restaurant
        $cat = $db->prepare("SELECT restaurant_id FROM categories WHERE id = ?");
        $cat->execute([$id]);
        $existing = $cat->fetch();
        if (!$existing) jsonError('Category not found', 404);

        Auth::requireRestaurantAccess((int) $existing['restaurant_id']);

        $body = getJsonBody();
        $fields = [];
        $params = [];

        foreach (['name_ar', 'name_en', 'image', 'featured_type'] as $field) {
            if (isset($body[$field])) {
                $fields[] = "$field = ?";
                $params[] = $body[$field];
            }
        }
        foreach (['is_featured', 'sort_order'] as $field) {
            if (isset($body[$field])) {
                $fields[] = "$field = ?";
                $params[] = (int) $body[$field];
            }
        }

        if (empty($fields)) jsonError('No fields to update');
        $params[] = $id;
        $db->prepare("UPDATE categories SET " . implode(', ', $fields) . " WHERE id = ?")->execute($params);

        $cat = $db->prepare("SELECT * FROM categories WHERE id = ?");
        $cat->execute([$id]);
        jsonResponse(['category' => $cat->fetch()]);
    }

    // DELETE
    if ($method === 'DELETE') {
        Auth::validateCsrf();
        $id = (int) ($_GET['id'] ?? 0);
        if (!$id) jsonError('ID is required');

        $cat = $db->prepare("SELECT restaurant_id FROM categories WHERE id = ?");
        $cat->execute([$id]);
        $existing = $cat->fetch();
        if (!$existing) jsonError('Category not found', 404);

        Auth::requireRestaurantAccess((int) $existing['restaurant_id']);

        $db->prepare("DELETE FROM categories WHERE id = ?")->execute([$id]);
        jsonResponse(['success' => true, 'message' => 'Category deleted']);
    }

    jsonError('Method not allowed', 405);
}
