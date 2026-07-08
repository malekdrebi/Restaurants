/**
 * Admin Dashboard — All event delegation, no inline onclick. v3
 */
console.log('ADMIN JS v4 LOADED');
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

var selectedRestaurantId = null;
var selectedRestaurantSlug = '';
var selectedCategoryId = null;
var selectedSubcategoryId = null;
var categories = [];
var currentItems = [];

// ═══ SINGLE EVENT DELEGATION FOR EVERYTHING ═══
document.addEventListener('click', function(e) {
    // Category edit button
    var catBtn = e.target.closest('.cat-edit-btn');
    if (catBtn) {
        e.preventDefault(); e.stopPropagation();
        var cid = catBtn.getAttribute('data-id');
        console.log('Edit category', cid);
        if (cid) showEditCategory(parseInt(cid));
        return;
    }
    // Category row — select (but not if edit button)
    var catRow = e.target.closest('.tree-cat-row');
    if (catRow && !e.target.closest('.cat-edit-btn')) {
        var ccid = catRow.getAttribute('data-cid');
        console.log('Select category', ccid);
        if (ccid) selectCategory(parseInt(ccid));
        return;
    }
    // Subcategory row
    var subRow = e.target.closest('.tree-sub-row');
    if (subRow) {
        var scid = subRow.getAttribute('data-cid');
        var ssid = subRow.getAttribute('data-sid');
        console.log('Select subcategory', scid, ssid);
        if (scid && ssid) selectSubcategory(parseInt(scid), parseInt(ssid));
        return;
    }
    // Item card
    var itemCard = e.target.closest('.item-card-clickable');
    if (itemCard) {
        var iid = itemCard.getAttribute('data-iid');
        console.log('Edit item', iid);
        if (iid) showEditItem(parseInt(iid));
        return;
    }
});

function init() {
    if (typeof ADMIN_ROLE !== 'undefined' && ADMIN_ROLE === 'restaurant_admin' && ADMIN_RESTAURANT_ID) {
        document.getElementById('restaurantSelect').value = ADMIN_RESTAURANT_ID;
        document.getElementById('restaurantSelect').disabled = true;
        onRestaurantChange();
    }
    var s = document.getElementById('restaurantSelect');
    if (s && s.options.length > 1 && !s.value) { s.selectedIndex = 1; onRestaurantChange(); }
}

async function onRestaurantChange() {
    var s = document.getElementById('restaurantSelect');
    selectedRestaurantId = s.value ? parseInt(s.value) : null;
    selectedRestaurantSlug = s.selectedOptions[0] ? s.selectedOptions[0].getAttribute('data-slug') : '';
    if (!selectedRestaurantId) return;
    await loadCategories();
}

async function loadCategories() {
    try {
        var r = await fetch(apiUrl('categories', {restaurant_id: selectedRestaurantId}));
        var d = await r.json();
        categories = d.categories || [];
        renderCategoryTree();
    } catch(e) { toast('Failed to load categories', 'error'); }
}

function renderCategoryTree() {
    var t = document.getElementById('categoryTree');
    if (!categories.length) {
        t.innerHTML = '<div class="tree-empty">No categories.<br><button class="btn btn-sm btn-gold add-cat-btn" style="margin-top:8px">+ Add Category</button></div>';
        return;
    }
    t.innerHTML = categories.map(function(c) {
        var act = (selectedCategoryId === c.id && !selectedSubcategoryId) ? ' active' : '';
        return '<div class="tree-category tree-cat-row' + act + '" data-cid="' + c.id + '">' +
            '<span>' + (c.name_en || c.name_ar) + (c.is_featured == 1 ? ' ⭐' : '') + '</span>' +
            '<button class="cat-edit-btn" data-id="' + c.id + '" style="margin-left:auto;background:none;border:1px solid #333;color:#999;cursor:pointer;font-size:0.7rem;padding:2px 8px;border-radius:4px">✎ Edit</button>' +
            '</div><div id="subcats-' + c.id + '"></div>';
    }).join('');
    categories.forEach(function(c) { loadSubcategoriesForTree(c.id); });
    if (!selectedCategoryId && categories.length > 0) selectCategory(categories[0].id);
}

async function loadSubcategoriesForTree(catId) {
    try {
        var r = await fetch(apiUrl('subcategories', {category_id: catId}));
        var d = await r.json();
        var subs = d.subcategories || [];
        var el = document.getElementById('subcats-' + catId);
        if (!el) return;
        el.innerHTML = subs.map(function(s) {
            var act = (selectedCategoryId === catId && selectedSubcategoryId === s.id) ? ' active' : '';
            return '<div class="tree-subcategory tree-sub-row' + act + '" data-cid="' + catId + '" data-sid="' + s.id + '">' + (s.name_en || s.name_ar) + '</div>';
        }).join('');
    } catch(e) {}
}

function selectCategory(catId) {
    selectedCategoryId = catId; selectedSubcategoryId = null; renderCategoryTree();
    loadItems(catId, null).then(function() {
        if (!currentItems.length) {
            fetch(apiUrl('subcategories', {category_id: catId})).then(function(r) { return r.json(); }).then(function(d) {
                if (d.subcategories && d.subcategories.length) selectSubcategory(catId, d.subcategories[0].id);
            });
        }
    });
}
function selectSubcategory(catId, subId) { selectedCategoryId = catId; selectedSubcategoryId = subId; renderCategoryTree(); loadItems(catId, subId); }

function showAddCategory() {
    if (!selectedRestaurantId) { toast('Select a restaurant', 'error'); return; }
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
    var c = categories.find(function(x) { return x.id === catId; });
    if (!c) return;
    document.getElementById('catId').value = c.id;
    document.getElementById('catNameAr').value = c.name_ar || '';
    document.getElementById('catNameEn').value = c.name_en || '';
    document.getElementById('catFeatured').checked = c.is_featured == 1;
    document.getElementById('catFeaturedType').value = c.featured_type || 'most_ordered';
    document.getElementById('catFeaturedType').disabled = c.is_featured != 1;
    document.getElementById('catSortOrder').value = c.sort_order || 0;
    document.getElementById('catModalTitle').textContent = 'Edit Category';
    document.getElementById('deleteCatBtn').style.display = 'inline-flex';
    document.getElementById('catModalOverlay').classList.add('show');
}
function closeCatModal() { document.getElementById('catModalOverlay').classList.remove('show'); }

async function saveCategory() {
    var catId = document.getElementById('catId').value;
    var isF = document.getElementById('catFeatured').checked;
    var body = { restaurant_id: selectedRestaurantId, name_ar: document.getElementById('catNameAr').value.trim(), name_en: document.getElementById('catNameEn').value.trim(), is_featured: isF ? 1 : 0, featured_type: isF ? document.getElementById('catFeaturedType').value : null, sort_order: parseInt(document.getElementById('catSortOrder').value) || 0 };
    if (!body.name_ar || !body.name_en) { toast('Names required', 'error'); return; }
    try {
        var u = catId ? apiUrl('categories', {id: catId}) : apiUrl('categories');
        var r = await fetch(u, { method: catId ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': CSRF_TOKEN }, body: JSON.stringify(body) });
        var d = await r.json();
        if (!r.ok) { toast(d.error, 'error'); return; }
        closeCatModal(); await loadCategories(); toast(catId ? 'Updated' : 'Created', 'success');
    } catch(e) { toast('Network error', 'error'); }
}
async function deleteCategory() {
    var id = document.getElementById('catId').value;
    if (!confirm('Delete category and all items?')) return;
    try {
        var r = await fetch(apiUrl('categories', {id: id}), { method: 'DELETE', headers: { 'X-CSRF-Token': CSRF_TOKEN } });
        if (!r.ok) { toast('Failed', 'error'); return; }
        closeCatModal(); selectedCategoryId = null; await loadCategories(); toast('Deleted', 'success');
    } catch(e) { toast('Network error', 'error'); }
}

// ── Items ──
async function loadItems(catId, subId) {
    var p = document.getElementById('mainPanel');
    p.innerHTML = '<div style="text-align:center;padding:60px"><div style="width:32px;height:32px;border:2px solid rgba(201,163,102,0.2);border-top-color:#C9A366;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto"></div></div>';
    try {
        var params = {category_id: catId}; if (subId) params.subcategory_id = subId;
        var r = await fetch(apiUrl('items', params)); var d = await r.json();
        currentItems = d.items || []; renderItems();
    } catch(e) { p.innerHTML = '<div class="panel-placeholder"><p>Failed to load items</p></div>'; }
}

function renderItems() {
    var p = document.getElementById('mainPanel');
    var c = categories.find(function(x) { return x.id === selectedCategoryId; });
    var cn = c ? (c.name_en || c.name_ar) : 'Items';
    if (!currentItems.length) {
        p.innerHTML = '<div class="panel-header"><h2>' + cn + '</h2><button class="btn btn-gold add-item-btn">+ Add Item</button></div><div class="panel-placeholder"><p>No items</p></div>';
        return;
    }
    var h = '<div class="panel-header"><h2>' + cn + ' <span style="color:var(--text-muted);font-size:0.8rem">(' + currentItems.length + ')</span></h2><button class="btn btn-gold add-item-btn">+ Add Item</button></div><div class="items-grid">';
    currentItems.forEach(function(item) {
        h += '<div class="item-card item-card-clickable" data-iid="' + item.id + '" style="cursor:pointer">' +
            (item.image ? '<img src="/' + item.image + '" class="item-card-img" alt="">' : '<div class="item-card-img placeholder">🍽</div>') +
            '<div class="item-card-body"><div class="item-card-name">' + (item.name_ar || '') + '<span class="en">' + (item.name_en || '') + '</span></div>' +
            '<div class="item-card-price">' + parseFloat(item.price).toFixed(3) + ' LYD</div>' +
            '<div class="item-card-meta">' +
            (item.spicy == 1 ? '<span class="badge badge-spicy">Spicy</span>' : '') +
            (item.recommended == 1 ? '<span class="badge badge-rec">Rec</span>' : '') +
            (item.variants && item.variants.length ? '<span class="badge badge-variants">' + item.variants.length + ' variants</span>' : '') +
            '</div></div></div>';
    });
    h += '</div>'; p.innerHTML = h;
}

function showAddItem() {
    if (!selectedCategoryId) { toast('Select a category', 'error'); return; }
    document.getElementById('itemId').value = '';
    document.getElementById('itemCategoryId').value = selectedCategoryId;
    document.getElementById('itemSubcategoryId').value = selectedSubcategoryId || '';
    document.getElementById('itemNameAr').value = ''; document.getElementById('itemNameEn').value = '';
    document.getElementById('itemDescAr').value = ''; document.getElementById('itemDescEn').value = '';
    document.getElementById('itemPrice').value = '0';
    document.getElementById('itemSortOrder').value = currentItems.length + 1;
    document.getElementById('itemSpicy').checked = false; document.getElementById('itemRecommended').checked = false;
    document.getElementById('itemImagePath').value = '';
    document.getElementById('itemImagePreview').style.display = 'none';
    document.getElementById('itemImageFile').value = '';
    document.getElementById('itemModalTitle').textContent = 'Add Item';
    document.getElementById('deleteItemBtn').style.display = 'none';
    document.getElementById('variantsList').innerHTML = '';
    document.getElementById('itemModalOverlay').classList.add('show');
}
function showEditItem(itemId) {
    var item = currentItems.find(function(i) { return i.id === itemId; });
    if (!item) return;
    document.getElementById('itemId').value = item.id;
    document.getElementById('itemCategoryId').value = item.category_id;
    document.getElementById('itemSubcategoryId').value = item.subcategory_id || '';
    document.getElementById('itemNameAr').value = item.name_ar || ''; document.getElementById('itemNameEn').value = item.name_en || '';
    document.getElementById('itemDescAr').value = item.desc_ar || ''; document.getElementById('itemDescEn').value = item.desc_en || '';
    document.getElementById('itemPrice').value = parseFloat(item.price) || 0;
    document.getElementById('itemSortOrder').value = item.sort_order || 0;
    document.getElementById('itemSpicy').checked = item.spicy == 1; document.getElementById('itemRecommended').checked = item.recommended == 1;
    document.getElementById('itemImagePath').value = item.image || ''; document.getElementById('itemImageFile').value = '';
    var pv = document.getElementById('itemImagePreview');
    if (item.image) { pv.src = '/' + item.image; pv.style.display = 'block'; } else { pv.style.display = 'none'; }
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
        reader.onload = function(e) { var pv = document.getElementById('itemImagePreview'); pv.src = e.target.result; pv.style.display = 'block'; };
        reader.readAsDataURL(input.files[0]);
    }
}

async function saveItem() {
    var itemId = document.getElementById('itemId').value;
    var imageFile = document.getElementById('itemImageFile').files[0];
    var imagePath = document.getElementById('itemImagePath').value;
    if (imageFile) {
        var fd = new FormData(); fd.append('image', imageFile); fd.append('restaurant_id', selectedRestaurantId); fd.append('restaurant_slug', selectedRestaurantSlug);
        try {
            var ur = await fetch(apiUrl('upload'), { method: 'POST', headers: { 'X-CSRF-Token': CSRF_TOKEN }, body: fd });
            var ud = await ur.json();
            if (!ur.ok) { toast(ud.error, 'error'); return; }
            imagePath = ud.path;
        } catch(e) { toast('Upload failed', 'error'); return; }
    }
    var body = { category_id: parseInt(document.getElementById('itemCategoryId').value), subcategory_id: document.getElementById('itemSubcategoryId').value ? parseInt(document.getElementById('itemSubcategoryId').value) : null, name_ar: document.getElementById('itemNameAr').value.trim(), name_en: document.getElementById('itemNameEn').value.trim(), price: parseFloat(document.getElementById('itemPrice').value) || 0, desc_ar: document.getElementById('itemDescAr').value.trim(), desc_en: document.getElementById('itemDescEn').value.trim(), image: imagePath || null, spicy: document.getElementById('itemSpicy').checked ? 1 : 0, recommended: document.getElementById('itemRecommended').checked ? 1 : 0, sort_order: parseInt(document.getElementById('itemSortOrder').value) || 0 };
    if (!body.name_ar || !body.name_en) { toast('Names required', 'error'); return; }
    try {
        var u = itemId ? apiUrl('items', {id: itemId}) : apiUrl('items');
        var r = await fetch(u, { method: itemId ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': CSRF_TOKEN }, body: JSON.stringify(body) });
        var d = await r.json();
        if (!r.ok) { toast(d.error, 'error'); return; }
        var sid = itemId || d.item.id;
        await saveVariants(sid);
        closeItemModal(); await loadItems(selectedCategoryId, selectedSubcategoryId); toast(itemId ? 'Updated' : 'Created', 'success');
    } catch(e) { toast('Network error', 'error'); }
}
async function deleteItem() {
    var id = document.getElementById('itemId').value;
    if (!confirm('Delete item?')) return;
    try {
        var r = await fetch(apiUrl('items', {id: id}), { method: 'DELETE', headers: { 'X-CSRF-Token': CSRF_TOKEN } });
        if (!r.ok) { toast('Failed', 'error'); return; }
        closeItemModal(); await loadItems(selectedCategoryId, selectedSubcategoryId); toast('Deleted', 'success');
    } catch(e) { toast('Network error', 'error'); }
}

// ── Variants ──
function renderVariantsInForm(variants) {
    var c = document.getElementById('variantsList');
    if (!variants || !variants.length) { c.innerHTML = '<p style="color:var(--text-muted);font-size:0.8rem">No variants</p>'; return; }
    c.innerHTML = variants.map(function(v) {
        return '<div class="variant-row" data-variant-id="' + (v.id || '') + '">' +
            '<input type="text" placeholder="AR Name" value="' + (v.name_ar || v.name || '') + '" data-field="name_ar">' +
            '<input type="text" placeholder="EN Name" value="' + (v.name_en || v.en_name || '') + '" data-field="name_en">' +
            '<input type="number" placeholder="Price" value="' + (v.price || '') + '" step="0.001" data-field="price" style="max-width:100px">' +
            '<button onclick="this.closest(\'.variant-row\').remove()" type="button">×</button></div>';
    }).join('');
}
function addVariantRow() {
    var c = document.getElementById('variantsList');
    if (c.querySelector('p')) c.innerHTML = '';
    var row = document.createElement('div'); row.className = 'variant-row';
    row.innerHTML = '<input type="text" placeholder="AR Name" data-field="name_ar"><input type="text" placeholder="EN Name" data-field="name_en"><input type="number" placeholder="Price" step="0.001" data-field="price" style="max-width:100px"><button onclick="this.closest(\'.variant-row\').remove()" type="button">×</button>';
    c.appendChild(row);
}
async function saveVariants(itemId) {
    var rows = document.querySelectorAll('#variantsList .variant-row');
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i], vid = row.getAttribute('data-variant-id');
        var na = (row.querySelector('[data-field="name_ar"]') || {}).value || '';
        var ne = (row.querySelector('[data-field="name_en"]') || {}).value || '';
        var pv = (row.querySelector('[data-field="price"]') || {}).value || '';
        if (!na.trim() && !ne.trim()) continue;
        var body = { item_id: itemId, name_ar: na.trim(), name_en: ne.trim(), price: pv !== '' ? parseFloat(pv) : null, sort_order: i };
        try { var u = vid ? apiUrl('variants', {id: vid}) : apiUrl('variants'); await fetch(u, { method: vid ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': CSRF_TOKEN }, body: JSON.stringify(body) }); } catch(e) {}
    }
}

// ── Add buttons ──
document.addEventListener('click', function(e) {
    if (e.target.closest('.add-cat-btn')) { showAddCategory(); return; }
    if (e.target.closest('.add-item-btn')) { showAddItem(); return; }
});

function previewMenu() {
    if (!selectedRestaurantSlug) { toast('Select a restaurant', 'error'); return; }
    window.open('/menu?slug=' + selectedRestaurantSlug, '_blank');
}

function toast(msg, type) {
    var c = document.getElementById('toastContainer');
    var el = document.createElement('div'); el.className = 'toast toast-' + (type || 'info'); el.textContent = msg;
    c.appendChild(el);
    setTimeout(function() { el.style.opacity = '0'; el.style.transition = 'opacity 0.3s'; }, 3000);
    setTimeout(function() { el.remove(); }, 3300);
}

// ── Start ──
(function() {
    if (document.readyState !== 'loading') init();
    else document.addEventListener('DOMContentLoaded', init);
})();
