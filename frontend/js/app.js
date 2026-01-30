/**
 * Art Studio Companion - Main Application
 */

const API_BASE = '';

// State
const state = {
    supplies: [],
    projects: [],
    artworks: [],
};

// Note: Data loading is handled by auth.js after authentication

// ===================
// API Functions
// ===================

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',  // Include cookies for authentication
        ...options,
    };
    
    if (options.body && typeof options.body === 'object') {
        config.body = JSON.stringify(options.body);
    }
    
    const response = await fetch(url, config);
    
    // Handle unauthorized response
    if (response.status === 401) {
        if (typeof showAuth === 'function') {
            showAuth();
        }
        throw new Error('Please log in to continue');
    }
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Request failed' }));
        throw new Error(error.error || 'Request failed');
    }
    return response.json();
}

// ===================
// Supplies
// ===================

async function loadSupplies() {
    try {
        const data = await apiRequest('/api/supplies');
        state.supplies = data.supplies;
        renderSupplies();
    } catch (error) {
        console.error('Failed to load supplies:', error);
    }
}

function renderSupplies() {
    const container = document.getElementById('supplies-list');
    
    if (state.supplies.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <p>No supplies yet</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.supplies.map(supply => {
        const status = getStockStatus(supply.quantity);
        const colors = supply.colors || [];
        const colorDots = colors.length > 0 
            ? colors.slice(0, 5).map(c => `<span class="supply-color-dot" style="background: ${c.hex}" title="${escapeHtml(c.name)}"></span>`).join('') 
            + (colors.length > 5 ? `<span class="supply-color-more">+${colors.length - 5}</span>` : '')
            : '';
        const colorNames = colors.length > 0 
            ? ` - ${colors.slice(0, 3).map(c => c.name).join(', ')}${colors.length > 3 ? '...' : ''}`
            : '';
        return `
            <div class="supply-item" onclick="viewSupply(${supply.id})">
                <div class="supply-status ${status}"></div>
                <div class="supply-color-dots">${colorDots}</div>
                <div class="supply-info">
                    <div class="supply-name">${escapeHtml(supply.name)}${colorNames}</div>
                    <div class="supply-brand">${escapeHtml(supply.brand || '')}</div>
                </div>
            </div>
        `;
    }).join('');
}

function getStockStatus(quantity) {
    if (quantity <= 0) return 'empty';
    if (quantity <= 2) return 'low';
    return 'plenty';
}

async function showLowStock() {
    try {
        const data = await apiRequest('/api/supplies/low-stock');
        state.supplies = data.supplies;
        renderSupplies();
        
        if (data.count === 0) {
            alert('All your supplies are well stocked! 🎉');
        } else {
            // Show which specific supplies are low
            const lowItems = data.supplies.map(s => {
                const status = s.quantity === 0 ? '(empty)' : `(${s.quantity} left)`;
                return `• ${s.name} ${status}`;
            }).join('\n');
            alert(`Low Stock Alert:\n\n${lowItems}`);
        }
    } catch (error) {
        console.error('Failed to load low stock:', error);
    }
}

function openAddSupplyModal() {
    // Common art supplies organized by category
    const supplyCategories = {
        'Paints': ['Acrylic Paint', 'Oil Paint', 'Watercolor', 'Gouache', 'Ink', 'Spray Paint'],
        'Drawing': ['Pencils', 'Colored Pencils', 'Charcoal', 'Pastels', 'Markers', 'Pens'],
        'Brushes': ['Round Brush', 'Flat Brush', 'Fan Brush', 'Detail Brush', 'Palette Knife'],
        'Surfaces': ['Canvas', 'Paper', 'Sketchbook', 'Wood Panel', 'Cardboard'],
        'Fiber Arts': ['Yarn', 'Thread', 'Fabric', 'Crochet Hook', 'Knitting Needles', 'Embroidery Hoop'],
        'Sculpting': ['Clay', 'Polymer Clay', 'Wire', 'Sculpting Tools', 'Armature'],
        'Other': ['Easel', 'Palette', 'Tape', 'Glue', 'Scissors', 'Ruler']
    };
    
    let checkboxesHtml = '';
    for (const [category, items] of Object.entries(supplyCategories)) {
        checkboxesHtml += `<div class="supply-category">
            <h4>${category}</h4>
            <div class="supply-checkbox-grid">
                ${items.map(item => `
                    <label class="supply-checkbox-item">
                        <input type="checkbox" name="supply-item" value="${item}" onchange="toggleSupplyDetails(this)">
                        <span>${item}</span>
                    </label>
                `).join('')}
            </div>
        </div>`;
    }
    
    openModal(`
        <div class="modal-header">
            <h3>Add Supplies</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <form onsubmit="handleAddSupplies(event)">
            <p class="form-hint" style="margin-bottom: 1rem;">Select the materials you have. You can add details for each item after selecting.</p>
            
            <div class="supply-categories-container">
                ${checkboxesHtml}
            </div>
            
            <div id="selected-supplies-details" class="selected-supplies-details"></div>
            
            <div class="form-group" style="margin-top: 1rem;">
                <label class="checkbox-label">
                    <input type="checkbox" id="add-custom-supply" onchange="toggleCustomSupply(this)">
                    <span>Add a custom supply not listed above</span>
                </label>
            </div>
            
            <div id="custom-supply-section" class="custom-supply-section hidden">
                <div class="form-group">
                    <label for="custom-supply-name">Custom Supply Name</label>
                    <input type="text" id="custom-supply-name" placeholder="Enter supply name...">
                </div>
            </div>
            
            <div class="form-actions">
                <button type="button" class="btn" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Add Selected Supplies</button>
            </div>
        </form>
    `);
}

function toggleSupplyDetails(checkbox) {
    const detailsContainer = document.getElementById('selected-supplies-details');
    const itemName = checkbox.value;
    const detailId = `detail-${itemName.replace(/\s+/g, '-').toLowerCase()}`;
    
    if (checkbox.checked) {
        // Add details section for this item
        const detailHtml = `
            <div class="supply-detail-item" id="${detailId}">
                <div class="supply-detail-header">
                    <strong>${itemName}</strong>
                    <button type="button" class="btn-small" onclick="toggleDetailExpand('${detailId}')">+ Add Details</button>
                </div>
                <div class="supply-detail-fields hidden" id="${detailId}-fields">
                    <div class="supply-detail-row">
                        <div class="form-group compact">
                            <label>Quantity</label>
                            <input type="number" name="${detailId}-qty" min="1" value="1" class="small-input">
                        </div>
                        <div class="form-group compact">
                            <label>Brand</label>
                            <input type="text" name="${detailId}-brand" placeholder="Optional" class="small-input">
                        </div>
                        <div class="form-group compact">
                            <label>Notes</label>
                            <input type="text" name="${detailId}-notes" placeholder="Optional" class="small-input">
                        </div>
                    </div>
                </div>
            </div>
        `;
        detailsContainer.insertAdjacentHTML('beforeend', detailHtml);
    } else {
        // Remove details section
        const detailElement = document.getElementById(detailId);
        if (detailElement) detailElement.remove();
    }
}

function toggleDetailExpand(detailId) {
    const fields = document.getElementById(`${detailId}-fields`);
    const btn = document.querySelector(`#${detailId} .btn-small`);
    if (fields.classList.contains('hidden')) {
        fields.classList.remove('hidden');
        btn.textContent = '− Hide Details';
    } else {
        fields.classList.add('hidden');
        btn.textContent = '+ Add Details';
    }
}

function toggleCustomSupply(checkbox) {
    const section = document.getElementById('custom-supply-section');
    if (checkbox.checked) {
        section.classList.remove('hidden');
    } else {
        section.classList.add('hidden');
    }
}

async function handleAddSupplies(event) {
    event.preventDefault();
    
    const selectedCheckboxes = document.querySelectorAll('input[name="supply-item"]:checked');
    const supplies = [];
    
    // Collect selected supplies with their details
    selectedCheckboxes.forEach(checkbox => {
        const itemName = checkbox.value;
        const detailId = `detail-${itemName.replace(/\s+/g, '-').toLowerCase()}`;
        
        const qtyInput = document.querySelector(`input[name="${detailId}-qty"]`);
        const brandInput = document.querySelector(`input[name="${detailId}-brand"]`);
        const notesInput = document.querySelector(`input[name="${detailId}-notes"]`);
        
        supplies.push({
            name: itemName,
            quantity: qtyInput ? parseInt(qtyInput.value) || 1 : 1,
            brand: brandInput ? brandInput.value || null : null,
            notes: notesInput ? notesInput.value || null : null,
            type: getSupplyType(itemName),
        });
    });
    
    // Add custom supply if specified
    const customName = document.getElementById('custom-supply-name')?.value;
    if (customName && document.getElementById('add-custom-supply').checked) {
        supplies.push({
            name: customName,
            quantity: 1,
            type: 'other',
        });
    }
    
    if (supplies.length === 0) {
        alert('Please select at least one supply');
        return;
    }
    
    try {
        // Add each supply
        for (const supply of supplies) {
            await apiRequest('/api/supplies', { method: 'POST', body: supply });
        }
        closeModal();
        loadSupplies();
    } catch (error) {
        alert('Failed to add supplies: ' + error.message);
    }
}

function getSupplyType(itemName) {
    const typeMap = {
        'paint': ['Acrylic Paint', 'Oil Paint', 'Watercolor', 'Gouache', 'Ink', 'Spray Paint'],
        'pencil': ['Pencils', 'Colored Pencils', 'Charcoal', 'Pastels', 'Markers', 'Pens'],
        'brush': ['Round Brush', 'Flat Brush', 'Fan Brush', 'Detail Brush', 'Palette Knife'],
        'canvas': ['Canvas', 'Wood Panel'],
        'paper': ['Paper', 'Sketchbook', 'Cardboard'],
        'yarn': ['Yarn', 'Thread'],
        'fabric': ['Fabric'],
        'needle': ['Crochet Hook', 'Knitting Needles', 'Embroidery Hoop'],
        'clay': ['Clay', 'Polymer Clay'],
        'tool': ['Sculpting Tools', 'Armature', 'Wire', 'Easel', 'Palette', 'Tape', 'Glue', 'Scissors', 'Ruler'],
    };
    
    for (const [type, items] of Object.entries(typeMap)) {
        if (items.includes(itemName)) return type;
    }
    return 'other';
}

async function handleAddSupply(event) {
    event.preventDefault();
    
    const supply = {
        name: document.getElementById('supply-name').value,
        quantity: parseInt(document.getElementById('supply-quantity').value) || 1,
        brand: document.getElementById('supply-brand').value || null,
        type: document.getElementById('supply-type').value || null,
        unit: document.getElementById('supply-unit').value || null,
        notes: document.getElementById('supply-notes').value || null,
    };
    
    try {
        await apiRequest('/api/supplies', { method: 'POST', body: supply });
        closeModal();
        loadSupplies();
    } catch (error) {
        alert('Failed to add supply: ' + error.message);
    }
}

// Track selected colors for current supply being edited
let selectedColors = [];

function viewSupply(id) {
    const supply = state.supplies.find(s => s.id === id);
    if (!supply) return;
    
    // Initialize selected colors from supply
    selectedColors = supply.colors || [];
    
    // Check if this supply type supports colors
    const colorTypes = ['paint', 'yarn', 'pencil', 'thread', 'ink'];
    const showColors = colorTypes.includes(supply.type);
    
    openModal(`
        <div class="modal-header">
            <h3>Edit Supply</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <form onsubmit="handleUpdateSupply(event, ${id})">
            <div class="form-group">
                <label for="edit-supply-name">Name</label>
                <input type="text" id="edit-supply-name" value="${escapeHtml(supply.name || '')}" required>
            </div>
            <div class="form-group">
                <label for="edit-supply-brand">Brand</label>
                <input type="text" id="edit-supply-brand" value="${escapeHtml(supply.brand || '')}" placeholder="e.g., Winsor & Newton">
            </div>
            <div class="form-group">
                <label for="edit-supply-type">Type</label>
                <select id="edit-supply-type" onchange="toggleColorSection()">
                    <option value="">Select type...</option>
                    <option value="paint" ${supply.type === 'paint' ? 'selected' : ''}>Paint</option>
                    <option value="brush" ${supply.type === 'brush' ? 'selected' : ''}>Brush</option>
                    <option value="canvas" ${supply.type === 'canvas' ? 'selected' : ''}>Canvas</option>
                    <option value="paper" ${supply.type === 'paper' ? 'selected' : ''}>Paper</option>
                    <option value="pencil" ${supply.type === 'pencil' ? 'selected' : ''}>Pencil/Pen</option>
                    <option value="yarn" ${supply.type === 'yarn' ? 'selected' : ''}>Yarn</option>
                    <option value="fabric" ${supply.type === 'fabric' ? 'selected' : ''}>Fabric</option>
                    <option value="needle" ${supply.type === 'needle' ? 'selected' : ''}>Needle/Hook</option>
                    <option value="clay" ${supply.type === 'clay' ? 'selected' : ''}>Clay</option>
                    <option value="ink" ${supply.type === 'ink' ? 'selected' : ''}>Ink</option>
                    <option value="thread" ${supply.type === 'thread' ? 'selected' : ''}>Thread</option>
                    <option value="tool" ${supply.type === 'tool' ? 'selected' : ''}>Tool</option>
                    <option value="other" ${supply.type === 'other' ? 'selected' : ''}>Other</option>
                </select>
            </div>
            <div id="color-section" class="form-group color-section ${showColors ? '' : 'hidden'}">
                <label>Colors <span class="optional">(click to add multiple)</span></label>
                <div id="selected-colors" class="selected-colors-container">
                    ${renderSelectedColors()}
                </div>
                <div class="add-color-row">
                    <input type="color" id="edit-supply-color-picker" value="#ffffff">
                    <input type="text" id="edit-supply-color-name" placeholder="Color name (e.g., Cadmium Red)">
                    <button type="button" class="btn btn-small btn-primary" onclick="addColor()">+ Add</button>
                </div>
                <div class="color-presets">
                    <span class="color-preset-label">Quick add:</span>
                    <div class="color-preset-grid">
                        ${getColorPresets().map(c => `
                            <button type="button" class="color-preset" style="background: ${c.hex}" title="${c.name}" onclick="addColorPreset('${c.name}', '${c.hex}')"></button>
                        `).join('')}
                    </div>
                </div>
            </div>
            <div class="form-group">
                <label for="edit-supply-quantity">Quantity</label>
                <div class="quantity-control">
                    <button type="button" class="btn btn-small" onclick="adjustQuantity(-1)">−</button>
                    <input type="number" id="edit-supply-quantity" min="0" max="999" value="${supply.quantity || 0}">
                    <button type="button" class="btn btn-small" onclick="adjustQuantity(1)">+</button>
                </div>
            </div>
            <div class="stock-status-buttons">
                <label>Quick Set:</label>
                <button type="button" class="btn btn-small btn-danger" onclick="setQuantity(0)">Out of Stock</button>
                <button type="button" class="btn btn-small btn-warning" onclick="setQuantity(2)">Low Stock</button>
                <button type="button" class="btn btn-small btn-success" onclick="setQuantity(10)">Well Stocked</button>
            </div>
            <div class="form-group">
                <label for="edit-supply-unit">Unit</label>
                <input type="text" id="edit-supply-unit" value="${escapeHtml(supply.unit || '')}" placeholder="e.g., tubes, skeins, sheets">
            </div>
            <div class="form-group">
                <label for="edit-supply-notes">Notes</label>
                <textarea id="edit-supply-notes" placeholder="Any additional details...">${escapeHtml(supply.notes || '')}</textarea>
            </div>
            <div class="form-actions">
                <button type="button" class="btn btn-danger" onclick="deleteSupply(${id})">Delete</button>
                <button type="button" class="btn" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Changes</button>
            </div>
        </form>
    `);
}

function renderSelectedColors() {
    if (selectedColors.length === 0) {
        return '<p class="empty-colors">No colors added yet</p>';
    }
    return selectedColors.map((color, index) => `
        <div class="selected-color-tag" style="border-left: 4px solid ${color.hex}">
            <span class="color-swatch" style="background: ${color.hex}"></span>
            <span class="color-name">${escapeHtml(color.name)}</span>
            <button type="button" class="remove-color" onclick="removeColor(${index})" title="Remove">&times;</button>
        </div>
    `).join('');
}

function addColor() {
    const hex = document.getElementById('edit-supply-color-picker').value;
    const name = document.getElementById('edit-supply-color-name').value.trim();
    
    if (!name) {
        alert('Please enter a color name');
        return;
    }
    
    // Check for duplicates
    if (selectedColors.some(c => c.name.toLowerCase() === name.toLowerCase())) {
        alert('This color is already added');
        return;
    }
    
    selectedColors.push({ name, hex });
    document.getElementById('selected-colors').innerHTML = renderSelectedColors();
    document.getElementById('edit-supply-color-name').value = '';
}

function addColorPreset(name, hex) {
    // Check for duplicates
    if (selectedColors.some(c => c.name.toLowerCase() === name.toLowerCase())) {
        return; // Already added
    }
    
    selectedColors.push({ name, hex });
    document.getElementById('selected-colors').innerHTML = renderSelectedColors();
}

function removeColor(index) {
    selectedColors.splice(index, 1);
    document.getElementById('selected-colors').innerHTML = renderSelectedColors();
}

function getColorPresets() {
    return [
        // Reds
        { name: 'Cadmium Red', hex: '#e63946' },
        { name: 'Crimson', hex: '#dc143c' },
        { name: 'Scarlet', hex: '#ff2400' },
        // Oranges
        { name: 'Orange', hex: '#ff6b35' },
        { name: 'Burnt Orange', hex: '#cc5500' },
        // Yellows
        { name: 'Cadmium Yellow', hex: '#ffd60a' },
        { name: 'Lemon Yellow', hex: '#fff44f' },
        { name: 'Gold', hex: '#ffd700' },
        // Greens
        { name: 'Viridian', hex: '#40826d' },
        { name: 'Sap Green', hex: '#507d2a' },
        { name: 'Forest Green', hex: '#228b22' },
        { name: 'Mint', hex: '#98fb98' },
        // Blues
        { name: 'Ultramarine', hex: '#3f00ff' },
        { name: 'Cobalt Blue', hex: '#0047ab' },
        { name: 'Cerulean', hex: '#007ba7' },
        { name: 'Navy', hex: '#000080' },
        { name: 'Sky Blue', hex: '#87ceeb' },
        // Purples
        { name: 'Purple', hex: '#800080' },
        { name: 'Violet', hex: '#8b00ff' },
        { name: 'Lavender', hex: '#e6e6fa' },
        // Pinks
        { name: 'Magenta', hex: '#ff00ff' },
        { name: 'Pink', hex: '#ffc0cb' },
        { name: 'Coral', hex: '#ff7f50' },
        // Browns
        { name: 'Burnt Sienna', hex: '#e97451' },
        { name: 'Raw Umber', hex: '#826644' },
        { name: 'Brown', hex: '#8b4513' },
        // Neutrals
        { name: 'Black', hex: '#000000' },
        { name: 'White', hex: '#ffffff' },
        { name: 'Gray', hex: '#808080' },
    ];
}

function toggleColorSection() {
    const type = document.getElementById('edit-supply-type').value;
    const colorTypes = ['paint', 'yarn', 'pencil', 'thread', 'ink'];
    const section = document.getElementById('color-section');
    
    if (colorTypes.includes(type)) {
        section.classList.remove('hidden');
    } else {
        section.classList.add('hidden');
    }
}

function adjustQuantity(delta) {
    const input = document.getElementById('edit-supply-quantity');
    const newVal = Math.max(0, Math.min(999, parseInt(input.value || 0) + delta));
    input.value = newVal;
}

function setQuantity(value) {
    document.getElementById('edit-supply-quantity').value = value;
}

async function handleUpdateSupply(event, id) {
    event.preventDefault();
    
    const updates = {
        name: document.getElementById('edit-supply-name').value,
        brand: document.getElementById('edit-supply-brand').value || null,
        type: document.getElementById('edit-supply-type').value || null,
        colors: selectedColors,
        quantity: parseInt(document.getElementById('edit-supply-quantity').value) || 0,
        unit: document.getElementById('edit-supply-unit').value || null,
        notes: document.getElementById('edit-supply-notes').value || null,
    };
    
    try {
        await apiRequest(`/api/supplies/${id}`, { method: 'PUT', body: updates });
        closeModal();
        loadSupplies();
    } catch (error) {
        alert('Failed to update supply: ' + error.message);
    }
}

async function deleteSupply(id) {
    if (!confirm('Delete this supply?')) return;
    
    try {
        await apiRequest(`/api/supplies/${id}`, { method: 'DELETE' });
        closeModal();
        loadSupplies();
    } catch (error) {
        alert('Failed to delete supply: ' + error.message);
    }
}

// ===================
// Projects
// ===================

async function loadProjects() {
    try {
        const data = await apiRequest('/api/projects');
        state.projects = data.projects;
        renderProjects();
    } catch (error) {
        console.error('Failed to load projects:', error);
    }
}

function renderProjects() {
    const container = document.getElementById('projects-list');
    
    if (state.projects.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <p>No projects yet</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.projects.map(project => `
        <div class="project-item">
            <div class="item-content" onclick="viewProject(${project.id})">
                <div class="project-title">${escapeHtml(project.title)}</div>
                <div class="project-status">${project.status}</div>
            </div>
            <button class="item-delete-btn" onclick="event.stopPropagation(); deleteProject(${project.id})" title="Delete project">🗑️</button>
        </div>
    `).join('');
}

function openNewProjectModal() {
    openModal(`
        <div class="modal-header">
            <h3>New Project</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <form onsubmit="handleCreateProject(event)">
            <div class="form-group">
                <label for="project-title">Title *</label>
                <input type="text" id="project-title" required>
            </div>
            <div class="form-group">
                <label for="project-description">Description</label>
                <textarea id="project-description"></textarea>
            </div>
            <div class="form-actions">
                <button type="button" class="btn" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Create Project</button>
            </div>
        </form>
    `);
}

async function handleCreateProject(event) {
    event.preventDefault();
    
    const project = {
        title: document.getElementById('project-title').value,
        description: document.getElementById('project-description').value || null,
    };
    
    try {
        await apiRequest('/api/projects', { method: 'POST', body: project });
        closeModal();
        loadProjects();
    } catch (error) {
        alert('Failed to create project: ' + error.message);
    }
}

function viewProject(id) {
    const project = state.projects.find(p => p.id === id);
    if (!project) return;
    
    const steps = project.steps || [];
    const stepsHtml = steps.length > 0 
        ? steps.map(s => `<li class="${s.completed ? 'completed' : ''}">${escapeHtml(s.instruction)}</li>`).join('')
        : '<li>No steps defined yet</li>';
    
    openModal(`
        <div class="modal-header">
            <h3>${escapeHtml(project.title)}</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="project-details">
            <p><strong>Status:</strong> ${project.status}</p>
            ${project.description ? `<p>${escapeHtml(project.description)}</p>` : ''}
            <h4>Steps</h4>
            <ol>${stepsHtml}</ol>
            ${project.session_notes ? `<h4>Notes</h4><p>${escapeHtml(project.session_notes)}</p>` : ''}
        </div>
        <div class="form-actions">
            <button class="btn btn-warning" onclick="deleteProject(${id})">Delete</button>
            <button class="btn btn-primary" onclick="closeModal()">Close</button>
        </div>
    `);
}

async function deleteProject(id) {
    if (!confirm('Delete this project?')) return;
    
    try {
        await apiRequest(`/api/projects/${id}`, { method: 'DELETE' });
        // Close modal if it's open
        const modal = document.getElementById('modal-overlay');
        if (modal && !modal.classList.contains('hidden')) {
            closeModal();
        }
        loadProjects();
    } catch (error) {
        alert('Failed to delete project: ' + error.message);
    }
}

// ===================
// Portfolio
// ===================

async function loadPortfolio() {
    try {
        const data = await apiRequest('/api/portfolio');
        state.artworks = data.artworks;
        renderPortfolio();
    } catch (error) {
        console.error('Failed to load portfolio:', error);
    }
}

function renderPortfolio() {
    const container = document.getElementById('portfolio-gallery');
    
    if (state.artworks.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1;">
                <div class="empty-state-icon">🖼️</div>
                <p>No artworks yet</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = state.artworks.map(artwork => `
        <div class="gallery-item" onclick="viewArtwork(${artwork.id})">
            ${artwork.image_path 
                ? `<img src="${escapeHtml(artwork.image_path)}" alt="${escapeHtml(artwork.title || 'Artwork')}">`
                : `<div class="gallery-placeholder">🎨</div>`
            }
        </div>
    `).join('');
}

function openAddArtworkModal() {
    openModal(`
        <div class="modal-header">
            <h3>Add Artwork</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <form onsubmit="handleAddArtwork(event)" enctype="multipart/form-data">
            <div class="form-group">
                <label for="artwork-title">Title</label>
                <input type="text" id="artwork-title" placeholder="Name your artwork">
            </div>
            <div class="form-group">
                <label for="artwork-file">Upload Image *</label>
                <input type="file" id="artwork-file" accept=".jpg,.jpeg,.png,.pdf" required>
                <small class="form-hint">Accepted formats: JPEG, PNG, PDF (max 16MB)</small>
            </div>
            <div class="form-group">
                <label for="artwork-medium">Medium</label>
                <input type="text" id="artwork-medium" placeholder="e.g., watercolor, oil, digital">
            </div>
            <div class="form-group">
                <label for="artwork-difficulty">Difficulty (1-5)</label>
                <select id="artwork-difficulty">
                    <option value="">Select...</option>
                    <option value="1">1 - Beginner</option>
                    <option value="2">2 - Easy</option>
                    <option value="3">3 - Intermediate</option>
                    <option value="4">4 - Advanced</option>
                    <option value="5">5 - Expert</option>
                </select>
            </div>
            <div class="form-group">
                <label for="artwork-notes">Notes</label>
                <textarea id="artwork-notes" placeholder="Add any notes about this piece..."></textarea>
            </div>
            <div class="form-group copyright-section">
                <h4>🔒 Copyright Protection</h4>
                <p class="form-hint">Your artwork is protected by default. Only you can view and access it.</p>
                <label class="checkbox-label">
                    <input type="checkbox" id="artwork-allow-sharing">
                    <span>Allow others to view this artwork (if shared)</span>
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" id="artwork-allow-download">
                    <span>Allow downloads</span>
                </label>
            </div>
            <div class="form-actions">
                <button type="button" class="btn" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Upload Artwork</button>
            </div>
        </form>
    `);
}

async function handleAddArtwork(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('artwork-file');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select an image file');
        return;
    }
    
    // Create FormData for file upload
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', document.getElementById('artwork-title').value || '');
    formData.append('medium', document.getElementById('artwork-medium').value || '');
    formData.append('difficulty', document.getElementById('artwork-difficulty').value || '');
    formData.append('notes', document.getElementById('artwork-notes').value || '');
    formData.append('allow_sharing', document.getElementById('artwork-allow-sharing').checked);
    formData.append('allow_download', document.getElementById('artwork-allow-download').checked);
    
    try {
        const response = await fetch('/api/portfolio', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        closeModal();
        loadPortfolio();
    } catch (error) {
        alert('Failed to add artwork: ' + error.message);
    }
}

function viewArtwork(id) {
    const artwork = state.artworks.find(a => a.id === id);
    if (!artwork) return;
    
    // Build copyright notice
    let copyrightHtml = '';
    if (artwork.is_copyrighted !== false) {
        copyrightHtml = `
            <div class="copyright-notice">
                <span class="copyright-icon">©</span>
                <span>${artwork.copyright_notice || 'All Rights Reserved'}</span>
            </div>
            <div class="copyright-permissions">
                <span class="${artwork.allow_sharing ? 'allowed' : 'restricted'}">
                    ${artwork.allow_sharing ? '✓ Sharing allowed' : '✗ No sharing'}
                </span>
                <span class="${artwork.allow_download ? 'allowed' : 'restricted'}">
                    ${artwork.allow_download ? '✓ Download allowed' : '✗ No download'}
                </span>
            </div>
        `;
    }
    
    openModal(`
        <div class="modal-header">
            <h3>${escapeHtml(artwork.title || 'Untitled')}</h3>
            <button class="modal-close" onclick="closeModal()">&times;</button>
        </div>
        <div class="artwork-details">
            ${artwork.image_path ? `<img src="${escapeHtml(artwork.image_path)}" style="max-width: 100%; border-radius: 8px; margin-bottom: 1rem;">` : ''}
            <p><strong>Medium:</strong> ${artwork.medium || 'Not specified'}</p>
            <p><strong>Difficulty:</strong> ${artwork.difficulty ? '★'.repeat(artwork.difficulty) + '☆'.repeat(5 - artwork.difficulty) : 'Not rated'}</p>
            ${artwork.notes ? `<p><strong>Notes:</strong> ${escapeHtml(artwork.notes)}</p>` : ''}
            ${copyrightHtml}
        </div>
        <div class="form-actions">
            <button class="btn btn-warning" onclick="deleteArtwork(${id})">Delete</button>
            <button class="btn btn-primary" onclick="closeModal()">Close</button>
        </div>
    `);
}

async function deleteArtwork(id) {
    if (!confirm('Delete this artwork?')) return;
    
    try {
        await apiRequest(`/api/portfolio/${id}`, { method: 'DELETE' });
        closeModal();
        loadPortfolio();
    } catch (error) {
        alert('Failed to delete artwork: ' + error.message);
    }
}

// ===================
// Modal Utilities
// ===================

function openModal(content) {
    document.getElementById('modal-content').innerHTML = content;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
}

// Close modal on overlay click
document.getElementById('modal-overlay')?.addEventListener('click', (e) => {
    if (e.target.id === 'modal-overlay') {
        closeModal();
    }
});

// ===================
// View All Functions
// ===================

async function viewAllSupplies() {
    try {
        const data = await apiRequest('/api/supplies');
        
        const suppliesHtml = data.supplies.length === 0
            ? '<p class="empty-message">No supplies yet</p>'
            : data.supplies.map(supply => `
                <div class="view-all-item">
                    <div class="item-content" onclick="viewSupply(${supply.id})">
                        <span class="supply-status-dot ${getStockStatus(supply.quantity)}"></span>
                        <span class="item-title">${escapeHtml(supply.name)}</span>
                        <span class="item-meta">${supply.brand || ''} • Qty: ${supply.quantity}</span>
                    </div>
                    <button class="item-delete-btn" onclick="event.stopPropagation(); deleteSupply(${supply.id})" title="Delete">🗑️</button>
                </div>
            `).join('');
        
        openModal(`
            <div class="modal-header">
                <h3>📦 All Supplies (${data.supplies.length})</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="view-all-list">
                ${suppliesHtml}
            </div>
            <div class="form-actions">
                <button class="btn btn-primary" onclick="openAddSupplyModal()">+ Add Supply</button>
                <button class="btn" onclick="closeModal()">Close</button>
            </div>
        `);
    } catch (error) {
        console.error('Error loading all supplies:', error);
    }
}

async function viewAllProjects() {
    try {
        const data = await apiRequest('/api/projects');
        
        const projectsHtml = data.projects.length === 0
            ? '<p class="empty-message">No projects yet</p>'
            : data.projects.map(project => `
                <div class="view-all-item">
                    <div class="item-content" onclick="viewProject(${project.id})">
                        <span class="item-title">${escapeHtml(project.title)}</span>
                        <span class="item-status status-${project.status}">${project.status}</span>
                    </div>
                    <button class="item-delete-btn" onclick="event.stopPropagation(); deleteProject(${project.id})" title="Delete">🗑️</button>
                </div>
            `).join('');
        
        openModal(`
            <div class="modal-header">
                <h3>📋 All Projects (${data.projects.length})</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="view-all-list">
                ${projectsHtml}
            </div>
            <div class="form-actions">
                <button class="btn btn-primary" onclick="openNewProjectModal()">+ New Project</button>
                <button class="btn" onclick="closeModal()">Close</button>
            </div>
        `);
    } catch (error) {
        console.error('Error loading all projects:', error);
    }
}

async function viewAllPortfolio() {
    try {
        const data = await apiRequest('/api/portfolio');
        
        const artworksHtml = data.artworks.length === 0
            ? '<p class="empty-message">No artworks yet</p>'
            : `<div class="view-all-gallery">
                ${data.artworks.map(artwork => `
                    <div class="view-all-artwork" onclick="viewArtwork(${artwork.id})">
                        ${artwork.image_path 
                            ? `<img src="${escapeHtml(artwork.image_path)}" alt="${escapeHtml(artwork.title || 'Artwork')}">`
                            : '<div class="artwork-placeholder">🖼️</div>'}
                        <div class="artwork-info">
                            <span class="item-title">${escapeHtml(artwork.title || 'Untitled')}</span>
                            <span class="item-meta">${artwork.medium || ''}</span>
                        </div>
                    </div>
                `).join('')}
            </div>`;
        
        openModal(`
            <div class="modal-header">
                <h3>🖼️ All Portfolio (${data.artworks.length})</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="view-all-list">
                ${artworksHtml}
            </div>
            <div class="form-actions">
                <button class="btn btn-primary" onclick="openAddArtworkModal()">+ Add Artwork</button>
                <button class="btn" onclick="closeModal()">Close</button>
            </div>
        `);
    } catch (error) {
        console.error('Error loading all portfolio:', error);
    }
}

// ===================
// Utilities
// ===================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
