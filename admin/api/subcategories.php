<?php
/**
 * Subcategory CRUD.
 */

function handleSubcategories(): void
{
    $method = $_SERVER['REQUEST_METHOD'];
    $db = Database::getInstance();

    // GET
    if ($method === 'GET') {
        $categoryId = (int) ($_GET['category_id'] ?? 0);
        if (!$categoryId) jsonError('category_id is required');

        // Verify access via parent category
        $cat = $db->prepare("SELECT c.restaurant_id FROM categories c WHERE c.id = ?");
        $cat->execute([$categoryId]);
        $category = $cat->fetch();
        if (!$category) jsonError('Category not found', 404);
        Auth::requireRestaurantAccess((int) $category['restaurant_id']);

        $stmt = $db->prepare("SELECT * FROM subcategories WHERE category_id = ? ORDER BY sort_order ASC");
        $stmt->execute([$categoryId]);
        jsonResponse(['subcategories' => $stmt->fetchAll()]);
    }

    // POST
    if ($method === 'POST') {
        Auth::validateCsrf();
        $body = getJsonBody();
        $categoryId = (int) ($body['category_id'] ?? 0);
        if (!$categoryId) jsonError('category_id is required');

        $cat = $db->prepare("SELECT restaurant_id FROM categories WHERE id = ?");
        $cat->execute([$categoryId]);
        $category = $cat->fetch();
        if (!$category) jsonError('Category not found', 404);
        Auth::requireRestaurantAccess((int) $category['restaurant_id']);

        $stmt = $db->prepare(
            "INSERT INTO subcategories (category_id, name_ar, name_en, sort_order) VALUES (?, ?, ?, ?)"
        );
        $stmt->execute([$categoryId, $body['name_ar'] ?? '', $body['name_en'] ?? '', (int) ($body['sort_order'] ?? 0)]);

        $id = $db->lastInsertId();
        $sub = $db->prepare("SELECT * FROM subcategories WHERE id = ?");
        $sub->execute([$id]);
        jsonResponse(['subcategory' => $sub->fetch()], 201);
    }

    // PUT
    if ($method === 'PUT') {
        Auth::validateCsrf();
        $id = (int) ($_GET['id'] ?? 0);
        if (!$id) jsonError('ID is required');

        $sub = $db->prepare("SELECT s.id, c.restaurant_id FROM subcategories s JOIN categories c ON s.category_id = c.id WHERE s.id = ?");
        $sub->execute([$id]);
        $existing = $sub->fetch();
        if (!$existing) jsonError('Subcategory not found', 404);
        Auth::requireRestaurantAccess((int) $existing['restaurant_id']);

        $body = getJsonBody();
        $fields = [];
        $params = [];
        foreach (['name_ar', 'name_en'] as $f) {
            if (isset($body[$f])) { $fields[] = "$f = ?"; $params[] = $body[$f]; }
        }
        foreach (['category_id', 'sort_order'] as $f) {
            if (isset($body[$f])) { $fields[] = "$f = ?"; $params[] = (int) $body[$f]; }
        }
        if (empty($fields)) jsonError('No fields to update');
        $params[] = $id;
        $db->prepare("UPDATE subcategories SET " . implode(', ', $fields) . " WHERE id = ?")->execute($params);

        $sub = $db->prepare("SELECT * FROM subcategories WHERE id = ?");
        $sub->execute([$id]);
        jsonResponse(['subcategory' => $sub->fetch()]);
    }

    // DELETE
    if ($method === 'DELETE') {
        Auth::validateCsrf();
        $id = (int) ($_GET['id'] ?? 0);
        if (!$id) jsonError('ID is required');

        $sub = $db->prepare("SELECT s.id, c.restaurant_id FROM subcategories s JOIN categories c ON s.category_id = c.id WHERE s.id = ?");
        $sub->execute([$id]);
        $existing = $sub->fetch();
        if (!$existing) jsonError('Subcategory not found', 404);
        Auth::requireRestaurantAccess((int) $existing['restaurant_id']);

        $db->prepare("DELETE FROM subcategories WHERE id = ?")->execute([$id]);
        jsonResponse(['success' => true, 'message' => 'Subcategory deleted']);
    }

    jsonError('Method not allowed', 405);
}
