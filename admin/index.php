<?php
/**
 * Admin Entry Point — Login + Dashboard in one file.
 * No .htaccess routing needed.
 *
 * GET /admin/index.php  → show login form or dashboard
 * POST /admin/index.php → handle login
 */

require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/Database.php';
require_once __DIR__ . '/../includes/Auth.php';
require_once __DIR__ . '/../includes/helpers.php';

// Start session
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// ── Handle Login POST ──
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'login') {
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';

    if (empty($username) || empty($password)) {
        $loginError = 'Username and password are required.';
    } else {
        $admin = Auth::login($username, $password);
        if ($admin) {
            header('Location: index.php');
            exit;
        } else {
            $loginError = 'Invalid username or password.';
        }
    }
}

// ── Handle Logout ──
if (isset($_GET['logout'])) {
    Auth::logout();
    header('Location: index.php');
    exit;
}

// ── Check if logged in ──
$admin = Auth::user();

// ── If NOT logged in, show login page ──
if (!$admin) {
    ?>
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Login — Lavina House</title>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root { --bg: #0d0d0d; --surface: #1a1a1a; --accent-gold: #C9A366; --text: #e0e0e0; --text-muted: #999; --danger: #e74c3c; }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: var(--bg); color: var(--text);
                font-family: 'Montserrat', 'Cairo', sans-serif;
                min-height: 100vh; display: flex; align-items: center; justify-content: center;
            }
            .login-card {
                background: var(--surface); border-radius: 16px; padding: 40px;
                width: 100%; max-width: 400px; border: 1px solid #2a2a2a;
            }
            .login-logo {
                text-align: center; font-size: 1.4rem; font-weight: 700;
                color: var(--accent-gold); margin-bottom: 6px; font-family: 'Cairo', sans-serif;
            }
            .login-subtitle { text-align: center; color: var(--text-muted); font-size: 0.85rem; margin-bottom: 28px; }
            .form-group { margin-bottom: 16px; }
            .form-group label {
                display: block; font-size: 0.8rem; font-weight: 600; color: var(--text-muted);
                margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px;
            }
            .form-group input {
                width: 100%; padding: 10px 14px; background: #222; border: 1px solid #333;
                border-radius: 8px; color: var(--text); font-size: 0.95rem; font-family: inherit; outline: none;
            }
            .form-group input:focus { border-color: var(--accent-gold); }
            .login-btn {
                width: 100%; padding: 12px; background: var(--accent-gold); color: #1a1a1a;
                border: none; border-radius: 8px; font-weight: 700; font-size: 0.95rem; cursor: pointer;
                font-family: inherit; margin-top: 8px;
            }
            .login-btn:hover { opacity: 0.9; }
            .error-msg { color: var(--danger); font-size: 0.82rem; margin-top: 12px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <div class="login-logo">Lavina House</div>
            <div class="login-subtitle">Admin Dashboard</div>
            <?php if (isset($loginError)): ?>
                <div class="error-msg"><?= htmlspecialchars($loginError) ?></div>
            <?php endif; ?>
            <form method="POST" action="index.php">
                <input type="hidden" name="action" value="login">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required autofocus>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="login-btn">Sign In</button>
            </form>
        </div>
    </body>
    </html>
    <?php
    exit;
}

// ── Logged in — Show Dashboard ──
// Get restaurants
$db = Database::getInstance();
if ($admin['role'] === 'super_admin') {
    $restaurants = $db->query("SELECT * FROM restaurants ORDER BY sort_order ASC")->fetchAll();
} else {
    $stmt = $db->prepare("SELECT * FROM restaurants WHERE id = ?");
    $stmt->execute([$admin['restaurant_id']]);
    $restaurants = $stmt->fetchAll();
}

$csrfToken = Auth::csrfToken();
?>
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard — Lavina House Admin</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Montserrat:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/admin.css">
</head>
<body>
    <!-- Top Bar -->
    <header class="topbar">
        <div class="topbar-brand">Lavina House <span class="topbar-label">Admin</span></div>
        <div class="topbar-center">
            <select id="restaurantSelect" class="restaurant-select" onchange="onRestaurantChange()">
                <option value="">Select restaurant...</option>
                <?php foreach ($restaurants as $r): ?>
                    <option value="<?= $r['id'] ?>" data-slug="<?= htmlspecialchars($r['slug']) ?>"><?= htmlspecialchars($r['name_en'] ?: $r['name_ar']) ?></option>
                <?php endforeach; ?>
                <?php if ($admin['role'] === 'super_admin'): ?>
                    <option value="new">+ New Restaurant</option>
                <?php endif; ?>
            </select>
            <?php if ($admin['role'] === 'super_admin'): ?>
                <button class="btn btn-sm btn-outline" onclick="showAdminModal()">👥 Admins</button>
            <?php endif; ?>
            <?php if ($admin['role'] === 'super_admin'): ?>
                <button class="btn btn-sm btn-outline" onclick="showRestaurantModal()">+ Restaurant</button>
                <button class="btn btn-sm btn-outline" onclick="if(selectedRestaurantId)showRestaurantModal(selectedRestaurantId);else toast('Select a restaurant first','error')">✎ Edit</button>
                <button class="btn btn-sm btn-outline" onclick="if(selectedRestaurantId)showGalleryModal();else toast('Select a restaurant first','error')">🖼 Gallery</button>
                <button class="btn btn-sm btn-outline" onclick="if(selectedRestaurantId)showVipModal();else toast('Select a restaurant first','error')">⭐ VIP</button>
            <?php endif; ?>
            <button class="btn btn-sm btn-outline" onclick="previewMenu()">👁 Preview</button>
            <span id="viewCount" style="color:var(--text-muted);font-size:0.75rem;margin-left:4px"></span>
        </div>
        <div class="topbar-right">
            <span class="topbar-user"><?= htmlspecialchars($admin['username']) ?> (<?= $admin['role'] ?>)</span>
            <a href="index.php?logout=1" class="btn btn-sm btn-ghost">Logout</a>
        </div>
    </header>

    <div class="dashboard-layout">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h3>Categories</h3>
                <button class="btn btn-sm btn-gold" onclick="showAddCategory()">+ Add</button>
            </div>
            <nav class="category-tree" id="categoryTree">
                <div class="tree-empty">Select a restaurant</div>
            </nav>
        </aside>
        <main class="main-panel" id="mainPanel">
            <div class="panel-placeholder">
                <div class="panel-placeholder-icon">📋</div>
                <p>Select a category from the sidebar</p>
            </div>
        </main>
    </div>

    <!-- Item Modal -->
    <div class="modal-overlay" id="itemModalOverlay">
        <div class="modal" id="itemModal">
            <div class="modal-header">
                <h3 id="itemModalTitle">Edit Item</h3>
                <button class="modal-close" onclick="closeItemModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="lang-tabs">
                    <button class="lang-tab active" onclick="switchItemTab('ar', this)">العربية</button>
                    <button class="lang-tab" onclick="switchItemTab('en', this)">English</button>
                </div>
                <form id="itemForm">
                    <input type="hidden" id="itemId">
                    <input type="hidden" id="itemCategoryId">
                    <input type="hidden" id="itemSubcategoryId">
                    <div class="tab-content" id="tab-ar">
                        <div class="form-group"><label>Arabic Name</label><input type="text" id="itemNameAr" required></div>
                        <div class="form-group"><label>Arabic Description</label><textarea id="itemDescAr" rows="3"></textarea></div>
                    </div>
                    <div class="tab-content" id="tab-en" style="display:none">
                        <div class="form-group"><label>English Name</label><input type="text" id="itemNameEn" required></div>
                        <div class="form-group"><label>English Description</label><textarea id="itemDescEn" rows="3"></textarea></div>
                    </div>
                    <div class="form-row">
                        <div class="form-group"><label>Price (LYD)</label><input type="number" id="itemPrice" step="0.001" min="0" required></div>
                        <div class="form-group"><label>Sort Order</label><input type="number" id="itemSortOrder" value="0" min="0"></div>
                    </div>
                    <div class="form-row form-checks">
                        <label class="check-label"><input type="checkbox" id="itemSpicy"> Spicy 🌶</label>
                        <label class="check-label"><input type="checkbox" id="itemRecommended"> Recommended ⭐</label>
                    </div>
                    <div class="form-group">
                        <label>Image</label>
                        <input type="file" id="itemImageFile" accept="image/*" onchange="previewItemImage(this)">
                        <div style="position:relative;display:inline-block">
                            <img id="itemImagePreview" class="image-preview" style="display:none" alt="Preview">
                            <button type="button" id="removeImageBtn" onclick="removeItemImage()" style="display:none;position:absolute;top:-8px;right:-8px;background:red;color:white;border:none;border-radius:50%;width:22px;height:22px;font-size:14px;line-height:1;cursor:pointer;padding:0">×</button>
                        </div>
                        <input type="hidden" id="itemImagePath">
                    </div>
                    <div class="variants-section">
                        <div class="variants-header">
                            <h4>Variants</h4>
                            <button type="button" class="btn btn-sm btn-gold" onclick="addVariantRow()">+ Add Variant</button>
                        </div>
                        <div id="variantsList" class="variants-list"></div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-ghost" onclick="closeItemModal()">Cancel</button>
                <button class="btn btn-danger" id="deleteItemBtn" style="display:none" onclick="deleteItem()">Delete</button>
                <button class="btn btn-gold" onclick="saveItem()">Save</button>
            </div>
        </div>
    </div>

    <!-- Category Modal -->
    <div class="modal-overlay" id="catModalOverlay">
        <div class="modal modal-sm" id="catModal">
            <div class="modal-header">
                <h3 id="catModalTitle">Edit Category</h3>
                <button class="modal-close" onclick="closeCatModal()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="catForm">
                    <input type="hidden" id="catId">
                    <div class="form-group"><label>Arabic Name</label><input type="text" id="catNameAr" required></div>
                    <div class="form-group"><label>English Name</label><input type="text" id="catNameEn" required></div>
                    <div class="form-row form-checks">
                        <label class="check-label"><input type="checkbox" id="catFeatured" onchange="document.getElementById('catFeaturedType').disabled=!this.checked"> Featured</label>
                        <select id="catFeaturedType" class="form-select" disabled>
                            <option value="most_ordered">Most Ordered</option>
                            <option value="fastest_ordered">Fastest Ordered</option>
                        </select>
                    </div>
                    <div class="form-group"><label>Sort Order</label><input type="number" id="catSortOrder" value="0" min="0"></div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-ghost" onclick="closeCatModal()">Cancel</button>
                <button class="btn btn-danger" id="deleteCatBtn" style="display:none" onclick="deleteCategory()">Delete</button>
                <button class="btn btn-gold" onclick="saveCategory()">Save</button>
            </div>
        </div>
    </div>

    <!-- Restaurant Modal -->
    <div class="modal-overlay" id="restaurantModalOverlay">
        <div class="modal modal-sm" id="restaurantModal">
            <div class="modal-header">
                <h3 id="restaurantModalTitle">New Restaurant</h3>
                <button class="modal-close" onclick="closeRestaurantModal()">&times;</button>
            </div>
            <div class="modal-body">
                <form id="restaurantForm">
                    <input type="hidden" id="restaurantId">
                    <div class="form-group"><label>Arabic Name</label><input type="text" id="restaurantNameAr" required></div>
                    <div class="form-group"><label>English Name</label><input type="text" id="restaurantNameEn" required></div>
                    <div class="form-group"><label>Slug (URL name)</label><input type="text" id="restaurantSlug" placeholder="e.g. lavina-tripoli"></div>
                    <div class="form-group"><label>Address (AR)</label><input type="text" id="restaurantAddressAr"></div>
                    <div class="form-group"><label>Address (EN)</label><input type="text" id="restaurantAddressEn"></div>
                    <div class="form-group"><label>Phone</label><input type="text" id="restaurantPhone"></div>
                    <div class="form-group"><label>Google Maps URL</label><input type="text" id="restaurantMapsUrl" placeholder="https://maps.google.com/..."></div>
                    <div class="form-group"><label>Logo</label><input type="file" id="restaurantLogoFile" accept="image/*"><input type="hidden" id="restaurantLogo"></div>
                    <div class="form-group"><label>Background Image</label><input type="file" id="restaurantBgFile" accept="image/*"><input type="hidden" id="restaurantBg"></div>
                    <div class="form-group"><label>Theme Color</label><input type="color" id="restaurantColor" value="#C9A366" style="width:60px;height:36px;border:none;cursor:pointer"></div>

                    <div class="toggle-row">
                        <label class="toggle-label"><span class="toggle-switch"><input type="checkbox" id="restIsActive" checked><span class="toggle-slider"></span></span> Restaurant Active</label>
                        <label class="toggle-label"><span class="toggle-switch"><input type="checkbox" id="restShowVip" checked><span class="toggle-slider"></span></span> VIP Lounge</label>
                        <label class="toggle-label"><span class="toggle-switch"><input type="checkbox" id="restShowGallery" checked><span class="toggle-slider"></span></span> Gallery</label>
                        <label class="toggle-label"><span class="toggle-switch"><input type="checkbox" id="restShowTutorial" checked><span class="toggle-slider"></span></span> Tutorial</label>
                        <label class="toggle-label"><span class="toggle-switch"><input type="checkbox" id="restShowCart" checked><span class="toggle-slider"></span></span> Add to Cart</label>
                        <label class="toggle-label"><span class="toggle-switch"><input type="checkbox" id="restShowParallax" checked><span class="toggle-slider"></span></span> Parallax BG</label>
                        <label class="toggle-label"><span class="toggle-switch"><input type="checkbox" id="restShowHub" checked><span class="toggle-slider"></span></span> Hub Screen</label>
                        <label class="toggle-label"><span class="toggle-switch"><input type="checkbox" id="restShowVipPrices" checked><span class="toggle-slider"></span></span> Show VIP Prices</label>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-ghost" onclick="closeRestaurantModal()">Cancel</button>
                <button class="btn btn-danger" id="deleteRestaurantBtn" style="display:none" onclick="deleteRestaurant()">Delete</button>
                <button class="btn btn-gold" onclick="saveRestaurant()">Save</button>
            </div>
        </div>
    </div>

    <!-- Admin Management Modal -->
    <div class="modal-overlay" id="adminModalOverlay">
        <div class="modal" id="adminModal">
            <div class="modal-header">
                <h3>Manage Admins</h3>
                <button class="modal-close" onclick="closeAdminModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div id="adminsList" style="margin-bottom:20px"></div>
                <hr style="border-color:#333;margin:16px 0">
                <h4 style="color:var(--accent-gold);margin-bottom:12px">Add New Admin</h4>
                <form id="adminForm">
                    <div class="form-group"><label>Username</label><input type="text" id="newAdminUsername" required></div>
                    <div class="form-group"><label>Password</label><input type="password" id="newAdminPassword" required minlength="6"></div>
                    <div class="form-group">
                        <label>Role</label>
                        <select id="newAdminRole">
                            <option value="restaurant_admin">Restaurant Admin</option>
                            <option value="super_admin">Super Admin</option>
                        </select>
                    </div>
                    <div class="form-group" id="newAdminRestaurantGroup">
                        <label>Restaurant</label>
                        <select id="newAdminRestaurantId"></select>
                    </div>
                    <button type="button" class="btn btn-gold" onclick="addAdmin()">Add Admin</button>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-ghost" onclick="closeAdminModal()">Close</button>
            </div>
        </div>
    </div>

    <!-- Gallery Modal -->
    <div class="modal-overlay" id="galleryModalOverlay">
        <div class="modal" id="galleryModal">
            <div class="modal-header">
                <h3>Gallery Images</h3>
                <button class="modal-close" onclick="closeGalleryModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div id="galleryImagesList" style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px"></div>
                <div class="form-group">
                    <label>Upload New Image</label>
                    <input type="file" id="galleryFile" accept="image/*">
                    <button class="btn btn-gold btn-sm" onclick="uploadGalleryImage()" style="margin-top:6px">Upload</button>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn btn-ghost" onclick="closeGalleryModal()">Close</button>
            </div>
        </div>
    </div>

    <!-- VIP Modal -->
    <div class="modal-overlay" id="vipModalOverlay">
        <div class="modal" id="vipModal">
            <div class="modal-header">
                <h3>VIP Lounge Items</h3>
                <button class="modal-close" onclick="closeVipModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div id="vipItemsList" style="margin-bottom:16px"></div>
                <hr style="border-color:#333;margin:14px 0">
                <h4 style="color:var(--accent-gold);margin-bottom:10px">Add VIP Item</h4>
                <form id="vipForm">
                    <div class="form-row">
                        <div class="form-group"><label>Title AR</label><input type="text" id="vipTitleAr"></div>
                        <div class="form-group"><label>Title EN</label><input type="text" id="vipTitleEn"></div>
                    </div>
                    <div class="form-row">
                        <div class="form-group"><label>Description AR</label><input type="text" id="vipDescAr"></div>
                        <div class="form-group"><label>Description EN</label><input type="text" id="vipDescEn"></div>
                    </div>
                    <div class="form-row">
                        <div class="form-group"><label>Price</label><input type="text" id="vipPrice" placeholder="e.g. 150 د.ل"></div>
                        <div class="form-group"><label>Image</label><input type="file" id="vipImageFile" accept="image/*"></div>
                    </div>
                    <button type="button" class="btn btn-gold btn-sm" onclick="addVipItem()">Add Item</button>
                </form>
            </div>
            <div class="modal-footer">
                <button class="btn btn-ghost" onclick="closeVipModal()">Close</button>
            </div>
        </div>
    </div>

    <div class="toast-container" id="toastContainer"></div>

    <script>
        // CSRF token from PHP
        const CSRF_TOKEN = <?= json_encode($csrfToken) ?>;
        const ADMIN_ROLE = <?= json_encode($admin['role']) ?>;
        const ADMIN_RESTAURANT_ID = <?= json_encode($admin['restaurant_id']) ?>;

        // Auto-select restaurant for restaurant_admin
        if (ADMIN_ROLE === 'restaurant_admin' && ADMIN_RESTAURANT_ID) {
            document.getElementById('restaurantSelect').value = ADMIN_RESTAURANT_ID;
            document.getElementById('restaurantSelect').disabled = true;
            setTimeout(onRestaurantChange, 100);
        }
    </script>
    <script src="assets/admin.js?v=29"></script>
</body>
</html>
