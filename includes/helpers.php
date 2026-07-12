<?php
/**
 * Utility helper functions.
 */

/**
 * Send a JSON response with proper headers.
 */
function jsonResponse($data, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-cache, must-revalidate');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit;
}

/**
 * Send an error JSON response.
 */
function jsonError(string $message, int $status = 400): void
{
    jsonResponse(['error' => $message], $status);
}

/**
 * Get JSON body from a POST/PUT request.
 */
function getJsonBody(): array
{
    $body = file_get_contents('php://input');
    $data = json_decode($body, true);
    return is_array($data) ? $data : [];
}

/**
 * Sanitize a string for output.
 */
function sanitize(?string $value): string
{
    return htmlspecialchars($value ?? '', ENT_QUOTES, 'UTF-8');
}

/**
 * Generate a URL-safe slug from text.
 */
function slugify(string $text): string
{
    // Transliterate Arabic to nothing (we use English name for slugs)
    $text = strtolower(trim($text));
    $text = preg_replace('/[^a-z0-9\s-]/', '', $text);
    $text = preg_replace('/[\s]+/', '-', $text);
    $text = preg_replace('/-+/', '-', $text);
    return trim($text, '-');
}

/**
 * Format a price with currency.
 */
function formatPrice(float $price, string $lang = 'ar'): string
{
    $currency = $lang === 'ar' ? CURRENCY_AR : CURRENCY_EN;

    // Remove trailing zeros but keep up to 3 decimal places
    $formatted = rtrim(rtrim(number_format($price, 3, '.', ''), '0'), '.');

    // If it's a whole number, show no decimals
    if (floor($price) == $price) {
        $formatted = number_format($price, 0, '.', '');
    }

    return $formatted . ' ' . $currency;
}

/**
 * Parse a price string like "45 د.ل" into a float.
 */
function parsePriceString(string $priceStr): float
{
    $cleaned = preg_replace('/[^\d.]/', '', $priceStr);
    return floatval($cleaned);
}

/**
 * Normalize an uploaded image filename.
 */
function normalizeImageName(string $originalName, string $restaurantSlug): string
{
    $ext = strtolower(pathinfo($originalName, PATHINFO_EXTENSION));
    $base = strtolower(pathinfo($originalName, PATHINFO_FILENAME));

    // Clean up the base name
    $base = preg_replace('/[^a-z0-9\s_-]/', '', $base);
    $base = preg_replace('/[\s_]+/', '_', $base);
    $base = trim($base, '_-');

    if (empty($base)) {
        $base = 'image_' . time();
    }

    return $base . '.' . $ext;
}

/**
 * Ensure a directory exists.
 */
function ensureDir(string $path): void
{
    if (!is_dir($path)) {
        mkdir($path, 0755, true);
    }
}
