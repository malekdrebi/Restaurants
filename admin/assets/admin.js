/**
 * Admin Dashboard — All event delegation, no inline onclick. v3
 */
// Admin Dashboard JS
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
    // Subcategory reorder (must come before .reorder-btn)
    if (e.target.closest('.sub-reorder')) {
        e.stopPropagation();
        var srb = e.target.closest('.sub-reorder');
        reorderSubcategory(parseInt(srb.getAttribute('data-sid')), parseInt(srb.getAttribute('data-cid')), srb.getAttribute('data-dir'));
        return;
    }
    // Item reorder (must come before .reorder-btn)
    if (e.target.closest('.item-reorder')) {
        e.stopPropagation();
        var irb = e.target.closest('.item-reorder');
        reorderItem(parseInt(irb.getAttribute('data-iid')), irb.getAttribute('data-dir'));
        return;
    }
    // Category reorder
    if (e.target.closest('.reorder-btn')) {
        var rb = e.target.closest('.reorder-btn');
        var dir = rb.getAttribute('data-dir');
        var cid = parseInt(rb.getAttribute('data-cid'));
        reorderCategory(cid, dir);
        return;
    }
    // Category edit button
    var catBtn = e.target.closest('.cat-edit-btn');
    if (catBtn) {
        e.preventDefault(); e.stopPropagation();
        var cid = catBtn.getAttribute('data-id');
        if (cid) showEditCategory(parseInt(cid));
        return;
    }
    // Category row — select (but not if edit button)
    var catRow = e.target.closest('.tree-cat-row');
    if (catRow && !e.target.closest('.cat-edit-btn')) {
        var ccid = catRow.getAttribute('data-cid');
        if (ccid) selectCategory(parseInt(ccid));
        return;
    }
    // Subcategory row
    var subRow = e.target.closest('.tree-sub-row');
    if (subRow) {
        var scid = subRow.getAttribute('data-cid');
        var ssid = subRow.getAttribute('data-sid');
        if (scid && ssid) selectSubcategory(parseInt(scid), parseInt(ssid));
        return;
    }
    // Item card
    var itemCard = e.target.closest('.item-card-clickable');
    if (itemCard) {
        var iid = itemCard.getAttribute('data-iid');
        if (iid) showEditItem(parseInt(iid));
        return;
    }
});

function init() {
    if (typeof ADMIN_ROLE !== 'undefined' && ADMIN_ROLE === 'restaurant_admin' && ADMIN_RESTAURANT_ID) {
        document.getElementById('restaurantSelect').value = ADMIN_RESTAURANT_ID;
        document.getElementById('restaurantSelect').disabled = true;
        onRestaurantChange();
        return;
    }
    var s = document.getElementById('restaurantSelect');
    // Restore last selected restaurant
    var lastId = sessionStorage.getItem('lastRestaurantId');
    if (lastId && s) {
        for (var i = 0; i < s.options.length; i++) {
            if (s.options[i].value === lastId) { s.selectedIndex = i; onRestaurantChange(); return; }
        }
    }
    if (s && s.options.length > 1 && !s.value) { s.selectedIndex = 1; onRestaurantChange(); }
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
    var scrollTop = t.scrollTop;
    if (!categories.length) {
        t.innerHTML = '<div class="tree-empty">No categories.<br><button class="btn btn-sm btn-gold add-cat-btn" style="margin-top:8px">+ Add Category</button></div>';
        return;
    }
    t.innerHTML = categories.map(function(c, i) {
        var act = (selectedCategoryId == c.id && !selectedSubcategoryId) ? ' active' : '';
        return '<div class="tree-category tree-cat-row' + act + '" data-cid="' + c.id + '">' +
            '<span>' + (c.name_en || c.name_ar) + (c.is_featured == 1 ? ' ⭐' : '') + '</span>' +
            '<span style="display:flex;gap:2px;margin-left:auto">' +
            (i > 0 ? '<button class="reorder-btn" data-dir="up" data-cid="'+c.id+'" title="Move up">↑</button>' : '') +
            (i < categories.length-1 ? '<button class="reorder-btn" data-dir="down" data-cid="'+c.id+'" title="Move down">↓</button>' : '') +
            '<button class="cat-edit-btn" data-id="' + c.id + '" style="background:none;border:1px solid #333;color:#999;cursor:pointer;font-size:0.7rem;padding:2px 6px;border-radius:4px">✎</button>' +
            '</span></div><div id="subcats-' + c.id + '"></div>';
    }).join('');
    categories.forEach(function(c) { loadSubcategoriesForTree(c.id); });
    t.scrollTop = scrollTop;
    if (!selectedCategoryId && categories.length > 0) selectCategory(parseInt(categories[0].id));
}

async function loadSubcategoriesForTree(catId) {
    try {
        var r = await fetch(apiUrl('subcategories', {category_id: catId}));
        var d = await r.json();
        var subs = d.subcategories || [];
        var el = document.getElementById('subcats-' + catId);
        if (!el) return;
        el.innerHTML = subs.map(function(s, i) {
            var act = (selectedCategoryId == catId && selectedSubcategoryId == s.id) ? ' active' : '';
            return '<div class="tree-subcategory tree-sub-row' + act + '" data-cid="' + catId + '" data-sid="' + s.id + '">' +
                '<span>' + (s.name_en || s.name_ar) + '</span>' +
                '<span style="display:flex;gap:2px;margin-left:auto">' +
                (i > 0 ? '<button class="reorder-btn sub-reorder" data-dir="up" data-sid="'+s.id+'" data-cid="'+catId+'" title="Move up">↑</button>' : '') +
                (i < subs.length-1 ? '<button class="reorder-btn sub-reorder" data-dir="down" data-sid="'+s.id+'" data-cid="'+catId+'" title="Move down">↓</button>' : '') +
                '</span></div>';
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
    var c = categories.find(function(x) { return x.id == catId; });
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
async function reorderCategory(catId, dir) {
    var idx = -1;
    for (var i = 0; i < categories.length; i++) { if (categories[i].id == catId) { idx = i; break; } }
    if (idx < 0) return;
    var swapIdx = dir === 'up' ? idx - 1 : idx + 1;
    if (swapIdx < 0 || swapIdx >= categories.length) return;
    var catA = categories[idx], catB = categories[swapIdx];
    try {
        var soA = parseInt(catA.sort_order) || idx;
        var soB = parseInt(catB.sort_order) || swapIdx;
        if (soA === soB) { soA = idx * 10; soB = swapIdx * 10; }
        await fetch(apiUrl('categories', {id: catA.id}), { method:'PUT', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify({sort_order: soB}) });
        await fetch(apiUrl('categories', {id: catB.id}), { method:'PUT', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify({sort_order: soA}) });
        await loadCategories();
    } catch(e) { toast('Reorder failed','error'); }
}

async function reorderItem(itemId, dir) {
    var idx = -1;
    for (var i = 0; i < currentItems.length; i++) { if (currentItems[i].id == itemId) { idx = i; break; } }
    if (idx < 0) return;
    var swapIdx = dir === 'up' ? idx - 1 : idx + 1;
    if (swapIdx < 0 || swapIdx >= currentItems.length) return;
    var itemA = currentItems[idx], itemB = currentItems[swapIdx];
    try {
        // Use sort_order values, normalizing if identical
        var soA = parseInt(itemA.sort_order) || idx;
        var soB = parseInt(itemB.sort_order) || swapIdx;
        if (soA === soB) { soA = idx * 10; soB = swapIdx * 10; }
        await fetch(apiUrl('items', {id: itemA.id}), { method:'PUT', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify({sort_order: soB}) });
        await fetch(apiUrl('items', {id: itemB.id}), { method:'PUT', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify({sort_order: soA}) });
        loadItems(selectedCategoryId, selectedSubcategoryId);
    } catch(e) { toast('Reorder failed','error'); }
}

async function reorderSubcategory(subId, catId, dir) {
    var r = await fetch(apiUrl('subcategories', {category_id: catId}));
    var d = await r.json();
    var subs = d.subcategories || [];
    var idx = -1;
    for (var i = 0; i < subs.length; i++) { if (subs[i].id == subId) { idx = i; break; } }
    if (idx < 0) return;
    var swapIdx = dir === 'up' ? idx - 1 : idx + 1;
    if (swapIdx < 0 || swapIdx >= subs.length) return;
    var subA = subs[idx], subB = subs[swapIdx];
    try {
        var soA = parseInt(subA.sort_order) || idx;
        var soB = parseInt(subB.sort_order) || swapIdx;
        if (soA === soB) { soA = idx * 10; soB = swapIdx * 10; }
        await fetch(apiUrl('subcategories', {id: subA.id}), { method:'PUT', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify({sort_order: soB}) });
        await fetch(apiUrl('subcategories', {id: subB.id}), { method:'PUT', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify({sort_order: soA}) });
        loadSubcategoriesForTree(catId);
    } catch(e) { toast('Reorder failed','error'); }
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
    var c = categories.find(function(x) { return x.id == selectedCategoryId; });
    var cn = c ? (c.name_en || c.name_ar) : 'Items';
    if (!currentItems.length) {
        p.innerHTML = '<div class="panel-header"><h2>' + cn + '</h2><button class="btn btn-gold add-item-btn">+ Add Item</button></div><div class="panel-placeholder"><p>No items</p></div>';
        return;
    }
    var h = '<div class="panel-header"><h2>' + cn + ' <span style="color:var(--text-muted);font-size:0.8rem">(' + currentItems.length + ')</span></h2><button class="btn btn-gold add-item-btn">+ Add Item</button></div><div class="items-grid">';
    currentItems.forEach(function(item, i) {
        h += '<div class="item-card item-card-clickable" data-iid="' + item.id + '" style="cursor:pointer">' +
            '<div style="display:flex;flex-direction:column;gap:2px;margin-right:4px">' +
            (i > 0 ? '<button class="reorder-btn item-reorder" data-dir="up" data-iid="'+item.id+'" title="Move up">↑</button>' : '') +
            (i < currentItems.length-1 ? '<button class="reorder-btn item-reorder" data-dir="down" data-iid="'+item.id+'" title="Move down">↓</button>' : '') +
            '</div>' +
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
    document.getElementById('removeImageBtn').style.display = 'none';
    document.getElementById('itemImageFile').value = '';
    document.getElementById('itemModalTitle').textContent = 'Add Item';
    document.getElementById('deleteItemBtn').style.display = 'none';
    document.getElementById('variantsList').innerHTML = '';
    document.getElementById('itemModalOverlay').classList.add('show');
}
function showEditItem(itemId) {
    var item = currentItems.find(function(i) { return i.id == itemId; });
    if (!item) { toast('Item not found', 'error'); return; }
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
    if (item.image) { pv.src = '/' + item.image; pv.style.display = 'block'; document.getElementById('removeImageBtn').style.display = 'block'; }
    else { pv.style.display = 'none'; document.getElementById('removeImageBtn').style.display = 'none'; }
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
        reader.onload = function(e) { var pv = document.getElementById('itemImagePreview'); pv.src = e.target.result; pv.style.display = 'block'; document.getElementById('removeImageBtn').style.display = 'block'; };
        reader.readAsDataURL(input.files[0]);
    }
}
function removeItemImage() {
    document.getElementById('itemImagePreview').style.display = 'none';
    document.getElementById('removeImageBtn').style.display = 'none';
    document.getElementById('itemImagePath').value = '';
    document.getElementById('itemImageFile').value = '';
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
            '<input type="number" placeholder="Price" step="0.001" value="' + (v.price || '') + '" data-field="price">' +
            '<div class="var-img-cell">' +
            '<input type="file" accept="image/*" data-field="image_file" style="font-size:0.62rem;max-width:90px" title="Upload">' +
            (v.image ? '<span style="position:relative"><img src="/' + v.image + '" style="width:34px;height:34px;object-fit:cover;border-radius:4px;border:1px solid #333"><button class="variant-img-remove-btn" type="button" style="position:absolute;top:-5px;right:-5px;background:red;color:white;border:none;border-radius:50%;width:16px;height:16px;font-size:10px;line-height:1;cursor:pointer;padding:0">×</button></span>' : '') +
            '</div>' +
            '<input type="hidden" data-field="image" value="' + (v.image || '') + '">' +
            '<button class="variant-remove-btn" type="button" style="text-align:center">×</button>' +
            '</div>';
    }).join('');
}
function addVariantRow() {
    var c = document.getElementById('variantsList');
    if (c.querySelector('p')) c.innerHTML = '';
    var row = document.createElement('div'); row.className = 'variant-row';
    row.innerHTML = '<input type="text" placeholder="AR Name" data-field="name_ar"><input type="text" placeholder="EN Name" data-field="name_en"><input type="number" placeholder="Price" step="0.001" data-field="price"><div class="var-img-cell"><input type="file" accept="image/*" data-field="image_file" style="font-size:0.62rem;max-width:90px" title="Upload"></div><input type="hidden" data-field="image" value=""><button class="variant-remove-btn" type="button">×</button>';
    c.appendChild(row);
}
async function saveVariants(itemId) {
    var rows = document.querySelectorAll('#variantsList .variant-row');
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i], vid = row.getAttribute('data-variant-id');
        var na = (row.querySelector('[data-field="name_ar"]') || {}).value || '';
        var ne = (row.querySelector('[data-field="name_en"]') || {}).value || '';
        var pv = (row.querySelector('[data-field="price"]') || {}).value || '';
        var imgInput = row.querySelector('[data-field="image"]');
        var imgPath = imgInput ? (imgInput.value || '') : '';
        var imgFile = row.querySelector('[data-field="image_file"]');

        // Upload variant image if file selected
        if (imgFile && imgFile.files && imgFile.files[0]) {
            var fd = new FormData(); fd.append('image', imgFile.files[0]);
            fd.append('restaurant_id', selectedRestaurantId); fd.append('restaurant_slug', selectedRestaurantSlug);
            try {
                var ur = await fetch(apiUrl('upload'), { method: 'POST', headers: { 'X-CSRF-Token': CSRF_TOKEN }, body: fd });
                var ud = await ur.json();
                if (ur.ok) imgPath = ud.path;
            } catch(e) {}
        }

        if (!na.trim() && !ne.trim()) continue;
        var body = { item_id: itemId, name_ar: na.trim(), name_en: ne.trim(), price: pv !== '' ? parseFloat(pv) : null, image: imgPath.trim() || null, sort_order: i };
        try { var u = vid ? apiUrl('variants', {id: vid}) : apiUrl('variants'); await fetch(u, { method: vid ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': CSRF_TOKEN }, body: JSON.stringify(body) }); } catch(e) {}
    }
}

// ── Add/Remove buttons ──
document.addEventListener('click', function(e) {
    if (e.target.closest('.add-cat-btn')) { showAddCategory(); return; }
    if (e.target.closest('.add-item-btn')) { showAddItem(); return; }
    if (e.target.closest('.variant-remove-btn')) { e.target.closest('.variant-row').remove(); return; }
    // VIP edit button
    if (e.target.closest('.vip-edit-btn')) {
        var vid = parseInt(e.target.closest('.vip-edit-btn').getAttribute('data-vid'));
        if (vid) { editVipItem(vid); switchVipTab('items', document.querySelectorAll('#vipModal .lang-tab')[1]); }
        return;
    }
    // VIP buttons (all use delegation to avoid CSP issues)
    if (e.target.closest('.remove-vip-hero-btn')) { removeVipHeroBg(); return; }
    if (e.target.closest('.save-vip-hero-btn')) { saveVipHero(); return; }
    if (e.target.closest('.add-vip-item-btn')) { addVipItem(); return; }
    if (e.target.closest('.upload-vip-carousel-btn')) { uploadVipCarousel(); return; }
    if (e.target.closest('.close-vip-modal-btn')) { closeVipModal(); return; }
    if (e.target.closest('.vip-tab-btn')) { var b = e.target.closest('.vip-tab-btn'); switchVipTab(b.getAttribute('data-tab'), b); return; }
    if (e.target.closest('.variant-img-remove-btn')) {
        var row = e.target.closest('.variant-row');
        row.querySelector('[data-field=\"image\"]').value = '';
        row.querySelector('[data-field=\"image_file\"]').value = '';
        var img = row.querySelector('img'); if (img) img.remove();
        e.target.closest('.variant-img-remove-btn').remove();
        return;
    }
});

// ── Restaurant Management ──
function onRestaurantChange() {
    var s = document.getElementById('restaurantSelect');
    if (s.value === 'new') { showRestaurantModal(); s.value = ''; return; }
    selectedRestaurantId = s.value ? parseInt(s.value) : null;
    selectedRestaurantSlug = s.selectedOptions[0] ? s.selectedOptions[0].getAttribute('data-slug') : '';
    selectedCategoryId = null; selectedSubcategoryId = null; currentItems = [];
    document.getElementById('mainPanel').innerHTML = '<div class="panel-placeholder"><div class="panel-placeholder-icon">📋</div><p>Select a category from the sidebar</p></div>';
    if (!selectedRestaurantId) return;
    sessionStorage.setItem('lastRestaurantId', selectedRestaurantId);
    // Update topbar name
    var topName = document.getElementById('topbarName');
    if (topName && s.selectedOptions[0]) topName.textContent = s.selectedOptions[0].text;
    // Show view count
    fetch(apiUrl('restaurants')).then(function(r){return r.json()}).then(function(d){
        var rest = (d.restaurants||[]).find(function(x){return x.id==selectedRestaurantId});
        if (rest) document.getElementById('viewCount').textContent = '👁 ' + (rest.view_count||0) + ' views';
    });
    loadCategories();
}

function showRestaurantModal(editId) {
    if (editId) {
        fetch(apiUrl('restaurants')).then(function(r){return r.json()}).then(function(d){
            var rest = (d.restaurants||[]).find(function(x){return x.id==editId});
            if(!rest) return;
            document.getElementById('restaurantId').value = rest.id;
            document.getElementById('restaurantNameAr').value = rest.name_ar||'';
            document.getElementById('restaurantNameEn').value = rest.name_en||'';
            document.getElementById('restaurantSlug').value = rest.slug||'';
            document.getElementById('restaurantAddressAr').value = rest.address_ar||'';
            document.getElementById('restaurantAddressEn').value = rest.address_en||'';
            document.getElementById('restaurantPhone').value = rest.phone||'';
            document.getElementById('restaurantMapsUrl').value = rest.maps_url||'';
            document.getElementById('restaurantHoursAr').value = rest.working_hours_ar||'';
            document.getElementById('restaurantHoursEn').value = rest.working_hours_en||'';
            document.getElementById('restaurantLogo').value = rest.logo||'';
            document.getElementById('restaurantBg').value = rest.bg_image||'';
            document.getElementById('vipHeroBgPath').value = rest.vip_hero_bg||'';
            if (rest.vip_hero_bg) {
                document.getElementById('vipHeroBgPreview').src = '/' + rest.vip_hero_bg;
                document.getElementById('vipHeroBgPreview').style.display = 'block';
                document.getElementById('vipHeroBgRemove').style.display = 'block';
            }
            var bgPv = document.getElementById('restaurantBgPreview');
            if (rest.bg_image) { bgPv.src = '/' + rest.bg_image; bgPv.style.display = 'block'; document.getElementById('restaurantBgRemove').style.display = 'block'; }
            else { bgPv.style.display = 'none'; document.getElementById('restaurantBgRemove').style.display = 'none'; }
            document.getElementById('restIsActive').checked = rest.is_active!=0;
            document.getElementById('restaurantColor').value = rest.primary_color||'#C9A366';
            document.getElementById('restShowVip').checked = rest.show_vip!=0;
            document.getElementById('restShowGallery').checked = rest.show_gallery!=0;
            document.getElementById('restShowTutorial').checked = rest.show_tutorial!=0;
            document.getElementById('restShowCart').checked = rest.show_cart!=0;
            document.getElementById('restShowParallax').checked = rest.show_parallax!=0;
            document.getElementById('restShowHub').checked = rest.show_hub!=0;
            document.getElementById('restShowVipPrices').checked = rest.show_vip_prices!=0;
            document.getElementById('restaurantModalTitle').textContent = 'Edit Restaurant';
            document.getElementById('deleteRestaurantBtn').style.display = 'inline-flex';
            document.getElementById('restaurantModalOverlay').classList.add('show');
        });
    } else {
        document.getElementById('restaurantId').value = '';
        document.getElementById('restaurantNameAr').value = '';
        document.getElementById('restaurantNameEn').value = '';
        document.getElementById('restaurantSlug').value = '';
        document.getElementById('restaurantAddressAr').value = '';
        document.getElementById('restaurantAddressEn').value = '';
        document.getElementById('restaurantPhone').value = '';
        document.getElementById('restaurantBg').value = '';
        document.getElementById('restaurantBgPreview').style.display = 'none';
        document.getElementById('restaurantBgRemove').style.display = 'none';
        document.getElementById('restaurantBgFile').value = '';
        document.getElementById('restaurantModalTitle').textContent = 'New Restaurant';
        document.getElementById('deleteRestaurantBtn').style.display = 'none';
        document.getElementById('restaurantModalOverlay').classList.add('show');
    }
}
function closeRestaurantModal() { document.getElementById('restaurantModalOverlay').classList.remove('show'); }

async function saveRestaurant() {
    var id = document.getElementById('restaurantId').value;
    var body = {
        name_ar: document.getElementById('restaurantNameAr').value.trim(),
        name_en: document.getElementById('restaurantNameEn').value.trim(),
        slug: document.getElementById('restaurantSlug').value.trim() || document.getElementById('restaurantNameEn').value.toLowerCase().replace(/\s+/g,'-').replace(/[^a-z0-9-]/g,''),
        address_ar: document.getElementById('restaurantAddressAr').value.trim(),
        address_en: document.getElementById('restaurantAddressEn').value.trim(),
        phone: document.getElementById('restaurantPhone').value.trim(),
        maps_url: document.getElementById('restaurantMapsUrl').value.trim(),
        working_hours_ar: document.getElementById('restaurantHoursAr').value.trim(),
        working_hours_en: document.getElementById('restaurantHoursEn').value.trim(),
        logo: document.getElementById('restaurantLogo').value,
        bg_image: document.getElementById('restaurantBg').value,
        primary_color: document.getElementById('restaurantColor').value,
        show_vip: document.getElementById('restShowVip').checked?1:0,
        show_gallery: document.getElementById('restShowGallery').checked?1:0,
        show_tutorial: document.getElementById('restShowTutorial').checked?1:0,
        show_cart: document.getElementById('restShowCart').checked?1:0,
        show_parallax: document.getElementById('restShowParallax').checked?1:0,
        show_hub: document.getElementById('restShowHub').checked?1:0,
        show_vip_prices: document.getElementById('restShowVipPrices').checked?1:0,
        is_active: document.getElementById('restIsActive').checked?1:0
    };
    // Upload logo if selected
    var logoF = document.getElementById('restaurantLogoFile').files[0];
    var bgF = document.getElementById('restaurantBgFile').files[0];
    if (logoF) {
        var fd = new FormData(); fd.append('image',logoF); fd.append('restaurant_id',selectedRestaurantId||0); fd.append('restaurant_slug',body.slug);
        try { var ur=await fetch(apiUrl('upload'),{method:'POST',headers:{'X-CSRF-Token':CSRF_TOKEN},body:fd}); var ud=await ur.json(); if(ur.ok) body.logo=ud.path; } catch(e){}
    }
    if (bgF) {
        var fd2 = new FormData(); fd2.append('image',bgF); fd2.append('restaurant_id',selectedRestaurantId||0); fd2.append('restaurant_slug',body.slug);
        try { var ur2=await fetch(apiUrl('upload'),{method:'POST',headers:{'X-CSRF-Token':CSRF_TOKEN},body:fd2}); var ud2=await ur2.json(); if(ur2.ok) body.bg_image=ud2.path; } catch(e){}
    }
    if (!body.name_ar || !body.name_en) { toast('Names required', 'error'); return; }
    try {
        var u = id ? apiUrl('restaurants', {id:id}) : apiUrl('restaurants');
        var r = await fetch(u, { method: id?'PUT':'POST', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify(body) });
        var d = await r.json();
        if (!r.ok) { toast(d.error,'error'); return; }
        closeRestaurantModal();
        sessionStorage.setItem('lastRestaurantId', id || selectedRestaurantId);
        location.reload();
    } catch(e) { toast('Network error','error'); }
}

async function deleteRestaurant() {
    var id = document.getElementById('restaurantId').value;
    if (!confirm('Delete this restaurant and ALL its data?')) return;
    try {
        var r = await fetch(apiUrl('restaurants',{id:id}), { method:'DELETE', headers:{'X-CSRF-Token':CSRF_TOKEN} });
        if (!r.ok) { toast('Failed','error'); return; }
        closeRestaurantModal();
        location.reload();
    } catch(e) { toast('Network error','error'); }
}

// ── Admin Management ──
async function showAdminModal() {
    document.getElementById('adminModalOverlay').classList.add('show');
    var r = await fetch(apiUrl('admins'));
    var d = await r.json();
    var admins = d.admins || [];
    var html = '<table style="width:100%;font-size:0.82rem"><tr style="color:var(--accent-gold)"><th>Username</th><th>Role</th><th>Restaurant</th><th></th></tr>';
    admins.forEach(function(a){
        html += '<tr style="border-top:1px solid #222"><td style="padding:6px 0">'+a.username+'</td><td>'+a.role+'</td><td>'+(a.restaurant_name_en||'-')+'</td><td><button class="btn btn-sm btn-ghost" onclick="deleteAdmin('+a.id+')">Delete</button></td></tr>';
    });
    html += '</table>';
    document.getElementById('adminsList').innerHTML = html;
    // Load restaurants for dropdown
    var rr = await fetch(apiUrl('restaurants'));
    var dd = await rr.json();
    var opts = (dd.restaurants||[]).map(function(x){return '<option value="'+x.id+'">'+x.name_en+'</option>'}).join('');
    document.getElementById('newAdminRestaurantId').innerHTML = opts;
}
function closeAdminModal() { document.getElementById('adminModalOverlay').classList.remove('show'); }

async function addAdmin() {
    var body = {
        username: document.getElementById('newAdminUsername').value.trim(),
        password: document.getElementById('newAdminPassword').value,
        role: document.getElementById('newAdminRole').value,
        restaurant_id: document.getElementById('newAdminRestaurantId').value || null
    };
    if (!body.username || !body.password) { toast('Username and password required','error'); return; }
    if (body.password.length < 6) { toast('Password must be 6+ chars','error'); return; }
    try {
        var r = await fetch(apiUrl('admins'), { method:'POST', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify(body) });
        var d = await r.json();
        if (!r.ok) { toast(d.error,'error'); return; }
        document.getElementById('newAdminUsername').value = '';
        document.getElementById('newAdminPassword').value = '';
        toast('Admin created!','success');
        showAdminModal();
    } catch(e) { toast('Network error','error'); }
}

async function deleteAdmin(id) {
    if (!confirm('Delete this admin?')) return;
    try {
        await fetch(apiUrl('admins',{id:id}), { method:'DELETE', headers:{'X-CSRF-Token':CSRF_TOKEN} });
        toast('Admin deleted','success');
        showAdminModal();
    } catch(e) { toast('Network error','error'); }
}

// ── Gallery Management ──
async function showGalleryModal() {
    document.getElementById('galleryModalOverlay').classList.add('show');
    var r = await fetch(apiUrl('gallery', {restaurant_id: selectedRestaurantId}));
    var d = await r.json();
    var images = d.images || [];
    var html = '';
    images.forEach(function(img) {
        html += '<div style="position:relative"><img src="/'+img.image_path+'" style="width:100px;height:80px;object-fit:cover;border-radius:6px;border:1px solid #333"><button style="position:absolute;top:-6px;right:-6px;background:red;color:white;border:none;border-radius:50%;width:20px;height:20px;font-size:12px;cursor:pointer" onclick="deleteGalleryImage('+img.id+')">×</button></div>';
    });
    if (!images.length) html = '<p style="color:var(--text-muted)">No gallery images yet</p>';
    document.getElementById('galleryImagesList').innerHTML = html;
}
function closeGalleryModal() { document.getElementById('galleryModalOverlay').classList.remove('show'); }

async function uploadGalleryImage() {
    var file = document.getElementById('galleryFile').files[0];
    if (!file) { toast('Select a file','error'); return; }
    var fd = new FormData(); fd.append('image',file); fd.append('restaurant_id',selectedRestaurantId);
    var r = await fetch(apiUrl('gallery'), { method:'POST', headers:{'X-CSRF-Token':CSRF_TOKEN}, body:fd });
    var d = await r.json();
    if (!r.ok) { toast(d.error,'error'); return; }
    document.getElementById('galleryFile').value = '';
    toast('Uploaded','success');
    showGalleryModal();
}
async function deleteGalleryImage(id) {
    if (!confirm('Delete this image?')) return;
    await fetch(apiUrl('gallery',{id:id}), { method:'DELETE', headers:{'X-CSRF-Token':CSRF_TOKEN} });
    toast('Deleted','success');
    showGalleryModal();
}

// ── VIP Management ──
async function showVipModal() {
    document.getElementById('vipModalOverlay').classList.add('show');
    var r = await fetch(apiUrl('vip_items', {restaurant_id: selectedRestaurantId}));
    var d = await r.json();
    var items = d.items || [];
    var html = '';
    items.forEach(function(item) {
        html += '<div style="display:flex;gap:10px;align-items:center;padding:8px;background:var(--surface2);border-radius:6px;margin-bottom:6px">';
        if (item.image_path) html += '<img src="/'+item.image_path+'" style="width:50px;height:50px;object-fit:cover;border-radius:4px">';
        html += '<div style="flex:1"><b>'+item.title_en+'</b><br><small style="color:var(--text-muted)">'+item.desc_en+' | '+item.price+'</small></div>';
        html += '<button class="btn btn-sm btn-ghost vip-edit-btn" data-vid="'+item.id+'">✎</button>';
        html += '<button class="btn btn-sm btn-ghost" onclick="deleteVipItem('+item.id+')">×</button></div>';
    });
    if (!items.length) html = '<p style="color:var(--text-muted)">No VIP items yet</p>';
    document.getElementById('vipItemsList').innerHTML = html;
    loadVipCarouselImages();
}
function switchVipTab(tab, btn) {
    document.querySelectorAll('#vipModal .lang-tab').forEach(function(t){t.classList.remove('active')});
    btn.classList.add('active');
    document.getElementById('vipTabHero').style.display = tab==='hero' ? 'block' : 'none';
    document.getElementById('vipTabItems').style.display = tab==='items' ? 'block' : 'none';
}
function previewVipHeroBg(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('vipHeroBgPreview').src = e.target.result;
            document.getElementById('vipHeroBgPreview').style.display = 'block';
            document.getElementById('vipHeroBgRemove').style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}
function removeVipHeroBg() {
    document.getElementById('vipHeroBgPreview').style.display = 'none';
    document.getElementById('vipHeroBgRemove').style.display = 'none';
    document.getElementById('vipHeroBgPath').value = '';
    document.getElementById('vipHeroBgFile').value = '';
}
async function loadVipCarouselImages() {
    if (!selectedRestaurantId) return;
    var r = await fetch(apiUrl('vip_carousel', {restaurant_id: selectedRestaurantId}));
    var d = await r.json();
    var imgs = d.images || [];
    var html = '';
    imgs.forEach(function(img) {
        html += '<div style="position:relative"><img src="/'+img.image_path+'" style="width:70px;height:55px;object-fit:cover;border-radius:4px;border:1px solid #333"><button onclick="deleteVipCarouselImage('+img.id+')" style="position:absolute;top:-5px;right:-5px;background:red;color:white;border:none;border-radius:50%;width:16px;height:16px;font-size:10px;cursor:pointer;padding:0">×</button></div>';
    });
    if (!imgs.length) html = '<span style="color:var(--text-muted);font-size:0.75rem">No carousel images</span>';
    document.getElementById('vipCarouselImagesList').innerHTML = html;
}
async function uploadVipCarousel() {
    var files = document.getElementById('vipCarouselFile').files;
    if (!files || !files.length) { toast('Select files','error'); return; }
    for (var i=0;i<files.length;i++) {
        var fd = new FormData(); fd.append('image',files[i]); fd.append('restaurant_id',selectedRestaurantId); fd.append('restaurant_slug',selectedRestaurantSlug);
        var ur = await fetch(apiUrl('upload'), { method:'POST', headers:{'X-CSRF-Token':CSRF_TOKEN}, body:fd });
        var ud = await ur.json();
        if (ur.ok) await fetch(apiUrl('vip_carousel'), { method:'POST', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify({restaurant_id:selectedRestaurantId, image_path: ud.path}) });
    }
    document.getElementById('vipCarouselFile').value = '';
    loadVipCarouselImages();
    toast('Carousel updated','success');
}
async function deleteVipCarouselImage(id) {
    await fetch(apiUrl('vip_carousel',{id:id}), { method:'DELETE', headers:{'X-CSRF-Token':CSRF_TOKEN} });
    loadVipCarouselImages();
}

async function saveVipHero() {
    var file = document.getElementById('vipHeroBgFile').files[0];
    if (!file) { toast('Select an image','error'); return; }
    if (!selectedRestaurantId) { toast('No restaurant selected','error'); return; }
    var fd = new FormData(); fd.append('image',file); fd.append('restaurant_id',selectedRestaurantId); fd.append('restaurant_slug',selectedRestaurantSlug);
    var r = await fetch(apiUrl('upload'), { method:'POST', headers:{'X-CSRF-Token':CSRF_TOKEN}, body:fd });
    var d = await r.json();
    if (!r.ok) { toast(d.error||'Upload failed','error'); return; }
    document.getElementById('vipHeroBgPath').value = d.path;
    var r2 = await fetch(apiUrl('restaurants', {id: selectedRestaurantId}), { method:'PUT', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify({vip_hero_bg: d.path}) });
    if (!r2.ok) { toast('Save failed','error'); return; }
    toast('Hero image saved','success');
}

function closeVipModal() { document.getElementById('vipModalOverlay').classList.remove('show'); document.getElementById('vipEditId').value = ''; document.querySelector('#vipForm .btn-gold').textContent = 'Add Item'; }


async function addVipItem() {
    var editId = document.getElementById('vipEditId').value;
    var body = {
        restaurant_id: selectedRestaurantId,
        title_ar: document.getElementById('vipTitleAr').value.trim(),
        title_en: document.getElementById('vipTitleEn').value.trim(),
        desc_ar: document.getElementById('vipDescAr').value.trim(),
        desc_en: document.getElementById('vipDescEn').value.trim(),
        price: document.getElementById('vipPrice').value.trim()
    };
    if (!body.title_ar || !body.title_en) { toast('Title required','error'); return; }
    var existingImg = document.getElementById('vipImagePath').value;
    if (existingImg) body.image_path = existingImg;
    var imgFile = document.getElementById('vipImageFile').files[0];
    if (imgFile) {
        var fd = new FormData(); fd.append('image',imgFile); fd.append('restaurant_id',selectedRestaurantId); fd.append('restaurant_slug',selectedRestaurantSlug);
        var ur = await fetch(apiUrl('upload'), { method:'POST', headers:{'X-CSRF-Token':CSRF_TOKEN}, body:fd });
        var ud = await ur.json();
        if (ur.ok) body.image_path = ud.path;
    }
    var method = editId ? 'PUT' : 'POST';
    var url = editId ? apiUrl('vip_items', {id: editId}) : apiUrl('vip_items');
    var r = await fetch(url, { method: method, headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify(body) });
    var d = await r.json();
    if (!r.ok) { toast(d.error,'error'); return; }
    // Upload extra images
    var itemId = editId || (d.item ? d.item.id : null);
    if (itemId) uploadVipExtraImages(itemId);
    document.getElementById('vipEditId').value = '';
    document.getElementById('vipTitleAr').value = '';
    document.getElementById('vipTitleEn').value = '';
    document.getElementById('vipDescAr').value = '';
    document.getElementById('vipDescEn').value = '';
    document.getElementById('vipPrice').value = '';
    document.getElementById('vipImageFile').value = '';
    document.getElementById('vipImagePath').value = '';
    document.getElementById('vipImagePreview').style.display = 'none';
    document.getElementById('vipImageRemove').style.display = 'none';
    document.querySelector('#vipForm .btn-gold').textContent = 'Add Item';
    toast(editId ? 'VIP item updated' : 'VIP item added','success');
    showVipModal();
}

function previewVipImage(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('vipImagePreview').src = e.target.result;
            document.getElementById('vipImagePreview').style.display = 'block';
            document.getElementById('vipImageRemove').style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}
function removeVipImage() {
    document.getElementById('vipImagePreview').style.display = 'none';
    document.getElementById('vipImageRemove').style.display = 'none';
    document.getElementById('vipImagePath').value = '';
    document.getElementById('vipImageFile').value = '';
}

async function editVipItem(id) {
    var r = await fetch(apiUrl('vip_items', {restaurant_id: selectedRestaurantId}));
    var d = await r.json();
    var item = (d.items||[]).find(function(x){return x.id==id});
    if (!item) return;
    document.getElementById('vipEditId').value = item.id;
    document.getElementById('vipTitleAr').value = item.title_ar||'';
    document.getElementById('vipTitleEn').value = item.title_en||'';
    document.getElementById('vipDescAr').value = item.desc_ar||'';
    document.getElementById('vipDescEn').value = item.desc_en||'';
    document.getElementById('vipPrice').value = item.price||'';
    document.getElementById('vipImagePath').value = item.image_path||'';
    var pv = document.getElementById('vipImagePreview');
    if (item.image_path) { pv.src = '/' + item.image_path; pv.style.display = 'block'; document.getElementById('vipImageRemove').style.display = 'block'; }
    else { pv.style.display = 'none'; document.getElementById('vipImageRemove').style.display = 'none'; }
    document.querySelector('#vipForm .btn-gold').textContent = 'Update Item';
    loadVipExtraImages(id);
}
async function uploadVipExtraImages(itemId) {
    var files = document.getElementById('vipExtraImages').files;
    if (!files || !files.length) return;
    for (var i = 0; i < files.length; i++) {
        var fd = new FormData(); fd.append('image', files[i]); fd.append('restaurant_id', selectedRestaurantId); fd.append('restaurant_slug', selectedRestaurantSlug);
        try {
            var ur = await fetch(apiUrl('upload'), { method:'POST', headers:{'X-CSRF-Token':CSRF_TOKEN}, body:fd });
            var ud = await ur.json();
            if (ur.ok) {
                await fetch(apiUrl('vip_item_images'), { method:'POST', headers:{'Content-Type':'application/json','X-CSRF-Token':CSRF_TOKEN}, body:JSON.stringify({vip_item_id: itemId, image_path: ud.path}) });
            }
        } catch(e) {}
    }
    document.getElementById('vipExtraImages').value = '';
}
async function deleteVipExtraImage(id) {
    if (!confirm('Delete image?')) return;
    await fetch(apiUrl('vip_item_images', {id:id}), { method:'DELETE', headers:{'X-CSRF-Token':CSRF_TOKEN} });
    toast('Deleted','success');
    // Refresh extra images list
    var vipId = document.getElementById('vipEditId').value;
    if (vipId) loadVipExtraImages(vipId);
}
async function loadVipExtraImages(vipItemId) {
    var r = await fetch(apiUrl('vip_item_images', {vip_item_id: vipItemId}));
    var d = await r.json();
    var imgs = d.images || [];
    var html = '';
    imgs.forEach(function(img) {
        html += '<div style="position:relative"><img src="/'+img.image_path+'" style="width:60px;height:50px;object-fit:cover;border-radius:4px;border:1px solid #333"><button onclick="deleteVipExtraImage('+img.id+')" style="position:absolute;top:-5px;right:-5px;background:red;color:white;border:none;border-radius:50%;width:16px;height:16px;font-size:10px;cursor:pointer;padding:0">×</button></div>';
    });
    if (!imgs.length) html = '<span style="color:var(--text-muted);font-size:0.75rem">No extra images</span>';
    document.getElementById('vipExtraImagesList').innerHTML = html;
}
async function deleteVipItem(id) {
    if (!confirm('Delete this VIP item?')) return;
    await fetch(apiUrl('vip_items',{id:id}), { method:'DELETE', headers:{'X-CSRF-Token':CSRF_TOKEN} });
    toast('Deleted','success');
    showVipModal();
}

function previewRestaurantBg(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('restaurantBgPreview').src = e.target.result;
            document.getElementById('restaurantBgPreview').style.display = 'block';
            document.getElementById('restaurantBgRemove').style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}
function removeRestaurantBg() {
    document.getElementById('restaurantBgPreview').style.display = 'none';
    document.getElementById('restaurantBgRemove').style.display = 'none';
    document.getElementById('restaurantBg').value = '';
    document.getElementById('restaurantBgFile').value = '';
}

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
