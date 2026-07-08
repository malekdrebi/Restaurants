/**
 * Admin Dashboard — Main Application Logic
 */
function apiUrl(endpoint, params) {
    var url = '/admin/api/' + endpoint + '.php';
    if (params) {
        var pairs = [];
        for (var k in params) {
            if (params.hasOwnProperty(k)) pairs.push(k + '=' + encodeURIComponent(params[k]));
        }
        if (pairs.length) url += '?' + pairs.join('&');
    }
    return url;
}

let selectedRestaurantId = null;
let selectedRestaurantSlug = '';
let selectedCategoryId = null;
let selectedSubcategoryId = null;
let categories = [];
let currentItems = [];

async function init() {
    if (ADMIN_ROLE === 'restaurant_admin' && ADMIN_RESTAURANT_ID) {
        document.getElementById('restaurantSelect').value = ADMIN_RESTAURANT_ID;
        document.getElementById('restaurantSelect').disabled = true;
        await onRestaurantChange();
    }
    var select = document.getElementById('restaurantSelect');
    if (select && select.options.length > 1 && !select.value) {
        select.selectedIndex = 1;
        await onRestaurantChange();
    }
}

async function onRestaurantChange() {
    var select = document.getElementById('restaurantSelect');
    selectedRestaurantId = select.value ? parseInt(select.value) : null;
    selectedRestaurantSlug = select.selectedOptions[0] ? select.selectedOptions[0].getAttribute('data-slug') : '';
    if (!selectedRestaurantId) return;
    await loadCategories();
}

// ── Categories ──
async function loadCategories() {
    try {
        var resp = await fetch(apiUrl('categories', {restaurant_id: selectedRestaurantId}));
        var data = await resp.json();
        categories = data.categories || [];
        renderCategoryTree();
    } catch(e) { toast('Failed to load categories', 'error'); }
}

function renderCategoryTree() {
    var tree = document.getElementById('categoryTree');
    if (!categories.length) {
        tree.innerHTML = '<div class="tree-empty">No categories yet.<br><button class="btn btn-sm btn-gold" style="margin-top:8px" onclick="showAddCategory()">+ Add First Category</button></div>';
        return;
    }
    tree.innerHTML = categories.map(function(cat) {
        return '<div class="tree-category' + (selectedCategoryId === cat.id && !selectedSubcategoryId ? ' active' : '') + '" data-cat-id="' + cat.id + '">' +
            '<span>' + (cat.name_en || cat.name_ar) + (cat.is_featured == 1 ? ' ⭐' : '') + '</span>' +
            '<span class="tree-actions"><button class="cat-edit-btn" data-cat-id="' + cat.id + '" title="Edit">✎</button></span>' +
            '</div><div id="subcats-' + cat.id + '"></div>';
    }).join('');
    // Load subcategories for all categories
    categories.forEach(function(cat) { loadSubcategoriesForTree(cat.id); });
    if (!selectedCategoryId && categories.length > 0) selectCategory(categories[0].id);
}

async function loadSubcategoriesForTree(catId) {
    try {
        var resp = await fetch(apiUrl('subcategories', {category_id: catId}));
        var data = await resp.json();
        var subs = data.subcategories || [];
        var el = document.getElementById('subcats-' + catId);
        if (!el) return;
        el.innerHTML = subs.map(function(sub) {
            return '<div class="tree-subcategory' + (selectedCategoryId === catId && selectedSubcategoryId === sub.id ? ' active' : '') +
                '" data-cat-id="' + catId + '" data-sub-id="' + sub.id + '">' + (sub.name_en || sub.name_ar) + '</div>';
        }).join('');
    } catch(e) {}
}

// Track which categories have subcategories (loaded in background)
var categoriesWithSubs = {};
function selectCategory(catId) { selectedCategoryId = catId; selectedSubcategoryId = null; renderCategoryTree(); loadItems(catId, null).then(function() { if (currentItems.length === 0) { fetch(apiUrl('subcategories', {category_id: catId})).then(function(r) { return r.json(); }).then(function(d) { var subs = d.subcategories || []; if (subs.length > 0) selectSubcategory(catId, subs[0].id); }); } }); }
function selectSubcategory(catId, subId) { selectedCategoryId = catId; selectedSubcategoryId = subId; renderCategoryTree(); loadItems(catId, subId); }

// Event delegation for tree clicks (categories + subcategories + edit buttons)
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('categoryTree').addEventListener('click', function(e) {
        // Edit category button
        if (e.target.closest('.cat-edit-btn')) {
            e.stopPropagation();
            var id = parseInt(e.target.closest('.cat-edit-btn').getAttribute('data-cat-id'));
            if (id) showEditCategory(id);
            return;
        }
        // Subcategory click
        var subDiv = e.target.closest('.tree-subcategory');
        if (subDiv) {
            var catId = parseInt(subDiv.getAttribute('data-cat-id'));
            var subId = parseInt(subDiv.getAttribute('data-sub-id'));
            if (catId && subId) selectSubcategory(catId, subId);
            return;
        }
        // Category click
        var catDiv = e.target.closest('.tree-category');
        if (catDiv) {
            var catId = parseInt(catDiv.getAttribute('data-cat-id'));
            if (catId) selectCategory(catId);
        }
    });

    // Event delegation for item edit buttons
    document.getElementById('mainPanel').addEventListener('click', function(e) {
        var editBtn = e.target.closest('.item-edit-btn');
        if (editBtn) {
            e.stopPropagation();
            var id = parseInt(editBtn.getAttribute('data-item-id'));
            if (id) showEditItem(id);
        }
    });
});

// ── Category CRUD ──
function showAddCategory() {
    if (!selectedRestaurantId) { toast('Select a restaurant first', 'error'); return; }
    document.getElementById('catId').value = '';
    document.getElementById('catNameAr').value = '';
    document.getElementById('catNameEn').value = '';
    document.getElementById('catFeatured').checked = false;
    document.getElementById('catFeaturedType').disabled = true;
    document.getElementById('catSortOrder').value = categories.length + 1;
    document.getElementById('catModalTitle').textContent = 'Add Category';
    document.getElementById('deleteCatBtn').style.display = 'none';
    document.getElementById('catModalOverlay').classList.add('show');
}

function showEditCategory(catId) {
    var cat = categories.find(function(c) { return c.id === catId; });
    if (!cat) return;
    document.getElementById('catId').value = cat.id;
    document.getElementById('catNameAr').value = cat.name_ar || '';
    document.getElementById('catNameEn').value = cat.name_en || '';
    document.getElementById('catFeatured').checked = cat.is_featured == 1;
    document.getElementById('catFeaturedType').value = cat.featured_type || 'most_ordered';
    document.getElementById('catFeaturedType').disabled = cat.is_featured != 1;
    document.getElementById('catSortOrder').value = cat.sort_order || 0;
    document.getElementById('catModalTitle').textContent = 'Edit Category';
    document.getElementById('deleteCatBtn').style.display = 'inline-flex';
    document.getElementById('catModalOverlay').classList.add('show');
}

function closeCatModal() { document.getElementById('catModalOverlay').classList.remove('show'); }

async function saveCategory() {
    var catId = document.getElementById('catId').value;
    var isFeatured = document.getElementById('catFeatured').checked;
    var body = {
        restaurant_id: selectedRestaurantId,
        name_ar: document.getElementById('catNameAr').value.trim(),
        name_en: document.getElementById('catNameEn').value.trim(),
        is_featured: isFeatured ? 1 : 0,
        featured_type: isFeatured ? document.getElementById('catFeaturedType').value : null,
        sort_order: parseInt(document.getElementById('catSortOrder').value) || 0
    };
    if (!body.name_ar || !body.name_en) { toast('Name fields are required', 'error'); return; }
    try {
        var url = catId ? apiUrl('categories', {id: catId}) : apiUrl('categories');
        var resp = await fetch(url, { method: catId ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': CSRF_TOKEN }, body: JSON.stringify(body) });
        var data = await resp.json();
        if (!resp.ok) { toast(data.error || 'Failed', 'error'); return; }
        closeCatModal();
        await loadCategories();
        toast(catId ? 'Category updated' : 'Category created', 'success');
    } catch(e) { toast('Network error', 'error'); }
}

async function deleteCategory() {
    var catId = document.getElementById('catId').value;
    if (!confirm('Delete this category and ALL its items?')) return;
    try {
        var resp = await fetch(apiUrl('categories', {id: catId}), { method: 'DELETE', headers: { 'X-CSRF-Token': CSRF_TOKEN } });
        if (!resp.ok) { var d = await resp.json(); toast(d.error || 'Failed', 'error'); return; }
        closeCatModal();
        selectedCategoryId = null;
        await loadCategories();
        toast('Category deleted', 'success');
    } catch(e) { toast('Network error', 'error'); }
}

// ── Items ──
async function loadItems(catId, subId) {
    var panel = document.getElementById('mainPanel');
    panel.innerHTML = '<div style="text-align:center;padding:60px"><div style="width:32px;height:32px;border:2px solid rgba(201,163,102,0.2);border-top-color:#C9A366;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto"></div></div>';
    try {
        var params = {category_id: catId};
        if (subId) params.subcategory_id = subId;
        var resp = await fetch(apiUrl('items', params));
        var data = await resp.json();
        currentItems = data.items || [];
        renderItems();
    } catch(e) { panel.innerHTML = '<div class="panel-placeholder"><p>Failed to load items</p></div>'; }
}

function renderItems() {
    var panel = document.getElementById('mainPanel');
    var cat = categories.find(function(c) { return c.id === selectedCategoryId; });
    var catName = cat ? (cat.name_en || cat.name_ar) : 'Items';
    if (!currentItems.length) {
        panel.innerHTML = '<div class="panel-header"><h2>' + catName + '</h2><button class="btn btn-gold" onclick="showAddItem()">+ Add Item</button></div><div class="panel-placeholder"><p>No items yet</p></div>';
        return;
    }
    var html = '<div class="panel-header"><h2>' + catName + ' <span style="color:var(--text-muted);font-size:0.8rem">(' + currentItems.length + ' items)</span></h2><button class="btn btn-gold" onclick="showAddItem()">+ Add Item</button></div><div class="items-grid">';
    currentItems.forEach(function(item) {
        html += '<div class="item-card">' +
            (item.image ? '<img src="/' + item.image + '" class="item-card-img" alt="" onerror="this.style.display=\'none\'">' : '<div class="item-card-img placeholder">🍽</div>') +
            '<div class="item-card-body"><div class="item-card-name">' + (item.name_ar || '') + '<span class="en">' + (item.name_en || '') + '</span></div>' +
            '<div class="item-card-price">' + parseFloat(item.price).toFixed(3) + ' LYD</div>' +
            '<div class="item-card-meta">' +
            (item.spicy == 1 ? '<span class="badge badge-spicy">Spicy</span>' : '') +
            (item.recommended == 1 ? '<span class="badge badge-rec">Recommended</span>' : '') +
            (item.variants && item.variants.length ? '<span class="badge badge-variants">' + item.variants.length + ' variants</span>' : '') +
            '</div></div><div class="item-card-actions"><button class="item-edit-btn" data-item-id="' + item.id + '">✎</button></div></div>';
    });
    html += '</div>';
    panel.innerHTML = html;
}

// ── Item Modal ──
function showAddItem() {
    if (!selectedCategoryId) { toast('Select a category first', 'error'); return; }
    document.getElementById('itemId').value = '';
    document.getElementById('itemCategoryId').value = selectedCategoryId;
    document.getElementById('itemSubcategoryId').value = selectedSubcategoryId || '';
    document.getElementById('itemNameAr').value = '';
    document.getElementById('itemNameEn').value = '';
    document.getElementById('itemDescAr').value = '';
    document.getElementById('itemDescEn').value = '';
    document.getElementById('itemPrice').value = '0';
    document.getElementById('itemSortOrder').value = currentItems.length + 1;
    document.getElementById('itemSpicy').checked = false;
    document.getElementById('itemRecommended').checked = false;
    document.getElementById('itemImagePath').value = '';
    document.getElementById('itemImagePreview').style.display = 'none';
    document.getElementById('itemImageFile').value = '';
    document.getElementById('itemModalTitle').textContent = 'Add Item';
    document.getElementById('deleteItemBtn').style.display = 'none';
    document.getElementById('variantsList').innerHTML = '';
    document.getElementById('itemModalOverlay').classList.add('show');
}

async function showEditItem(itemId) {
    var item = currentItems.find(function(i) { return i.id === itemId; });
    if (!item) return;
    document.getElementById('itemId').value = item.id;
    document.getElementById('itemCategoryId').value = item.category_id;
    document.getElementById('itemSubcategoryId').value = item.subcategory_id || '';
    document.getElementById('itemNameAr').value = item.name_ar || '';
    document.getElementById('itemNameEn').value = item.name_en || '';
    document.getElementById('itemDescAr').value = item.desc_ar || '';
    document.getElementById('itemDescEn').value = item.desc_en || '';
    document.getElementById('itemPrice').value = parseFloat(item.price) || 0;
    document.getElementById('itemSortOrder').value = item.sort_order || 0;
    document.getElementById('itemSpicy').checked = item.spicy == 1;
    document.getElementById('itemRecommended').checked = item.recommended == 1;
    document.getElementById('itemImagePath').value = item.image || '';
    document.getElementById('itemImageFile').value = '';
    var preview = document.getElementById('itemImagePreview');
    if (item.image) { preview.src = '/' + item.image; preview.style.display = 'block'; }
    else { preview.style.display = 'none'; }
    document.getElementById('itemModalTitle').textContent = 'Edit Item';
    document.getElementById('deleteItemBtn').style.display = 'inline-flex';
    renderVariantsInForm(item.variants || []);
    document.getElementById('itemModalOverlay').classList.add('show');
}

function closeItemModal() { document.getElementById('itemModalOverlay').classList.remove('show'); }

function switchItemTab(lang, btn) {
    document.querySelectorAll('.lang-tab').forEach(function(t) { t.classList.remove('active'); });
    btn.classList.add('active');
    document.getElementById('tab-ar').style.display = lang === 'ar' ? 'block' : 'none';
    document.getElementById('tab-en').style.display = lang === 'en' ? 'block' : 'none';
}

function previewItemImage(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var preview = document.getElementById('itemImagePreview');
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

async function saveItem() {
    var itemId = document.getElementById('itemId').value;
    var imageFile = document.getElementById('itemImageFile').files[0];
    var imagePath = document.getElementById('itemImagePath').value;

    if (imageFile) {
        var fd = new FormData();
        fd.append('image', imageFile);
        fd.append('restaurant_id', selectedRestaurantId);
        fd.append('restaurant_slug', selectedRestaurantSlug);
        try {
            var uploadResp = await fetch(apiUrl('upload'), { method: 'POST', headers: { 'X-CSRF-Token': CSRF_TOKEN }, body: fd });
            var uploadData = await uploadResp.json();
            if (!uploadResp.ok) { toast(uploadData.error || 'Upload failed', 'error'); return; }
            imagePath = uploadData.path;
        } catch(e) { toast('Image upload failed', 'error'); return; }
    }

    var body = {
        category_id: parseInt(document.getElementById('itemCategoryId').value),
        subcategory_id: document.getElementById('itemSubcategoryId').value ? parseInt(document.getElementById('itemSubcategoryId').value) : null,
        name_ar: document.getElementById('itemNameAr').value.trim(),
        name_en: document.getElementById('itemNameEn').value.trim(),
        price: parseFloat(document.getElementById('itemPrice').value) || 0,
        desc_ar: document.getElementById('itemDescAr').value.trim(),
        desc_en: document.getElementById('itemDescEn').value.trim(),
        image: imagePath || null,
        spicy: document.getElementById('itemSpicy').checked ? 1 : 0,
        recommended: document.getElementById('itemRecommended').checked ? 1 : 0,
        sort_order: parseInt(document.getElementById('itemSortOrder').value) || 0
    };
    if (!body.name_ar || !body.name_en) { toast('Name fields are required', 'error'); return; }

    try {
        var url = itemId ? apiUrl('items', {id: itemId}) : apiUrl('items');
        var resp = await fetch(url, { method: itemId ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': CSRF_TOKEN }, body: JSON.stringify(body) });
        var data = await resp.json();
        if (!resp.ok) { toast(data.error || 'Failed', 'error'); return; }
        var savedId = itemId || data.item.id;
        await saveVariants(savedId);
        closeItemModal();
        await loadItems(selectedCategoryId, selectedSubcategoryId);
        toast(itemId ? 'Item updated' : 'Item created', 'success');
    } catch(e) { toast('Network error', 'error'); }
}

async function deleteItem() {
    var itemId = document.getElementById('itemId').value;
    if (!confirm('Delete this item?')) return;
    try {
        var resp = await fetch(apiUrl('items', {id: itemId}), { method: 'DELETE', headers: { 'X-CSRF-Token': CSRF_TOKEN } });
        if (!resp.ok) { var d = await resp.json(); toast(d.error || 'Failed', 'error'); return; }
        closeItemModal();
        await loadItems(selectedCategoryId, selectedSubcategoryId);
        toast('Item deleted', 'success');
    } catch(e) { toast('Network error', 'error'); }
}

// ── Variants ──
function renderVariantsInForm(variants) {
    var container = document.getElementById('variantsList');
    if (!variants || !variants.length) { container.innerHTML = '<p style="color:var(--text-muted);font-size:0.8rem">No variants</p>'; return; }
    container.innerHTML = variants.map(function(v) {
        return '<div class="variant-row" data-variant-id="' + (v.id || '') + '">' +
            '<input type="text" placeholder="AR Name" value="' + (v.name_ar || v.name || '') + '" data-field="name_ar">' +
            '<input type="text" placeholder="EN Name" value="' + (v.name_en || v.en_name || '') + '" data-field="name_en">' +
            '<input type="number" placeholder="Price" value="' + (v.price || '') + '" step="0.001" data-field="price" style="max-width:100px">' +
            '<button onclick="this.closest(\'.variant-row\').remove()" title="Remove">×</button></div>';
    }).join('');
}

function addVariantRow() {
    var container = document.getElementById('variantsList');
    if (container.querySelector('p')) container.innerHTML = '';
    var row = document.createElement('div');
    row.className = 'variant-row';
    row.innerHTML = '<input type="text" placeholder="AR Name" data-field="name_ar">' +
        '<input type="text" placeholder="EN Name" data-field="name_en">' +
        '<input type="number" placeholder="Price" step="0.001" data-field="price" style="max-width:100px">' +
        '<button onclick="this.closest(\'.variant-row\').remove()" title="Remove">×</button>';
    container.appendChild(row);
}

async function saveVariants(itemId) {
    var rows = document.querySelectorAll('#variantsList .variant-row');
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var variantId = row.getAttribute('data-variant-id');
        var nameAr = (row.querySelector('[data-field="name_ar"]') || {}).value || '';
        var nameEn = (row.querySelector('[data-field="name_en"]') || {}).value || '';
        var priceVal = (row.querySelector('[data-field="price"]') || {}).value || '';
        if (!nameAr.trim() && !nameEn.trim()) continue;
        var body = { item_id: itemId, name_ar: nameAr.trim(), name_en: nameEn.trim(), price: priceVal !== '' ? parseFloat(priceVal) : null, sort_order: i };
        try {
            var url = variantId ? apiUrl('variants', {id: variantId}) : apiUrl('variants');
            await fetch(url, { method: variantId ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': CSRF_TOKEN }, body: JSON.stringify(body) });
        } catch(e) {}
    }
}

function previewMenu() {
    if (!selectedRestaurantSlug) { toast('Select a restaurant first', 'error'); return; }
    window.open('/menu?slug=' + selectedRestaurantSlug, '_blank');
}

function toast(message, type) {
    var container = document.getElementById('toastContainer');
    var el = document.createElement('div');
    el.className = 'toast toast-' + (type || 'info');
    el.textContent = message;
    container.appendChild(el);
    setTimeout(function() { el.style.opacity = '0'; el.style.transition = 'opacity 0.3s'; }, 3000);
    setTimeout(function() { el.remove(); }, 3300);
}

document.addEventListener('DOMContentLoaded', init);
