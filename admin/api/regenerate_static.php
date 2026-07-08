<?php
/**
 * Static HTML fallback generator.
 *
 * Called after admin saves data. Reads the menu.html template,
 * injects the current menu JSON data directly into it,
 * and writes the result to static/{slug}.html.
 *
 * This ensures the customer menu works even if the API/DB is down.
 */

require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/Database.php';
require_once __DIR__ . '/../../includes/helpers.php';
require_once __DIR__ . '/../../api/menu.php';

function regenerateStatic(int $restaurantId): bool
{
    $db = Database::getInstance();

    // Get restaurant slug
    $stmt = $db->prepare("SELECT slug, name_ar, name_en FROM restaurants WHERE id = ?");
    $stmt->execute([$restaurantId]);
    $restaurant = $stmt->fetch();

    if (!$restaurant) {
        error_log("Static regen: Restaurant #{$restaurantId} not found");
        return false;
    }

    $slug = $restaurant['slug'];

    // Get menu data
    $menuData = getMenuData($db, $slug);

    if (!$menuData) {
        error_log("Static regen: Could not get menu data for {$slug}");
        return false;
    }

    // Read the menu.html template
    $templatePath = __DIR__ . '/../../menu.html';
    if (!file_exists($templatePath)) {
        error_log("Static regen: menu.html template not found");
        return false;
    }

    $html = file_get_contents($templatePath);

    // Replace the API-fetch-based menu loading with embedded data
    // Pattern: Find the loadMenu function and replace menuData assignment with static data
    $menuJson = json_encode($menuData['menu'], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

    // Replace the loadMenu function body: override menuData directly instead of fetching
    $staticScript = <<<JS
        // ── STATIC FALLBACK: Embedded menu data (no API needed) ──
        (function() {
            // Override loadMenu to use embedded data
            const _embeddedMenu = {$menuJson};
            const _embeddedRestaurant = {
                slug: "{$restaurant['slug']}",
                name_ar: "{$restaurant['name_ar']}",
                name_en: "{$restaurant['name_en']}"
            };

            // Replace loadMenu to use embedded data
            window._staticMenuData = _embeddedMenu;
            window._staticRestaurantInfo = _embeddedRestaurant;
        })();
JS;

    // Insert the static script right after the loadMenu definition
    // Find: "async function loadMenu()" and insert static data before the fetch
    $html = str_replace(
        'async function loadMenu() {',
        "async function loadMenu() {\n            // STATIC FALLBACK: Use embedded data if available\n            if (window._staticMenuData && window._staticRestaurantInfo) {\n                menuData = window._staticMenuData;\n                restaurantInfo = window._staticRestaurantInfo;\n                updateRestaurantHeader();\n                const savedLang = localStorage.getItem('lavina_language');\n                if (savedLang) setLang(savedLang, false);\n                renderCategories();\n                renderMenu();\n                updateCartUI();\n                return;\n            }\n",
        $html
    );

    // Add the static script before the closing </script> tag of the last script block
    // Find the last </script> before </body>
    $pos = strrpos($html, '</script>');
    if ($pos !== false) {
        $html = substr_replace($html, $staticScript . "\n        \n    ", $pos, 0);
    }

    // Write the static file
    ensureDir(STATIC_DIR);
    $outputPath = STATIC_DIR . '/' . $slug . '.html';

    if (file_put_contents($outputPath, $html) === false) {
        error_log("Static regen: Failed to write {$outputPath}");
        return false;
    }

    error_log("Static regen: Generated {$outputPath} (" . strlen($html) . " bytes)");
    return true;
}
