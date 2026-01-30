/**
 * Authentication handling for Art Studio Companion
 */

let currentUser = null;
let currentConversationId = null;
let isGuest = false;

// Check auth status on page load
document.addEventListener('DOMContentLoaded', checkAuthStatus);

async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/me', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            isGuest = false;
            
            if (!currentUser.onboarding_completed) {
                showOnboarding();
            } else {
                showApp();
            }
        } else {
            showAuth();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        showAuth();
    }
}

function showAuth() {
    document.getElementById('auth-screen').classList.remove('hidden');
    document.getElementById('onboarding-screen').classList.add('hidden');
    document.getElementById('app-container').classList.add('hidden');
    showWelcomeForm();
}

function showWelcomeForm() {
    document.getElementById('welcome-form').classList.remove('hidden');
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.add('hidden');
    hideAuthError();
}

function showOnboarding() {
    document.getElementById('auth-screen').classList.add('hidden');
    document.getElementById('onboarding-screen').classList.remove('hidden');
    document.getElementById('app-container').classList.add('hidden');
}

function showApp() {
    document.getElementById('auth-screen').classList.add('hidden');
    document.getElementById('onboarding-screen').classList.add('hidden');
    document.getElementById('app-container').classList.remove('hidden');
    
    // Update user display and auth button
    const userDisplay = document.getElementById('user-display');
    const authBtn = document.getElementById('auth-btn');
    
    if (isGuest) {
        userDisplay.textContent = 'Guest Mode';
        authBtn.textContent = 'Create Account';
        authBtn.onclick = () => {
            showAuth();
            showRegisterForm();
        };
    } else {
        userDisplay.textContent = `Hello, ${currentUser.username}!`;
        authBtn.textContent = 'Sign Out';
        authBtn.onclick = handleLogout;
    }
    
    // Load user data (for guests, data won't persist)
    if (!isGuest) {
        loadConversations();
        loadSupplies();
        loadProjects();
        loadPortfolio();
        loadIdeas();
    } else {
        // Clear lists for guest mode
        document.getElementById('conversations-list').innerHTML = '<p class="empty-message">Sign in to save conversations</p>';
        document.getElementById('supplies-list').innerHTML = '<p class="empty-message">Add your first supply!</p>';
        document.getElementById('projects-list').innerHTML = '<p class="empty-message">No projects yet</p>';
        document.getElementById('portfolio-gallery').innerHTML = '<p class="empty-message">No artworks yet</p>';
        document.getElementById('ideas-list').innerHTML = '<p class="empty-message">Sign in to save ideas</p>';
    }
}

function continueAsGuest() {
    isGuest = true;
    currentUser = { username: 'Guest' };
    showOnboarding();
}

function showLoginForm() {
    document.getElementById('welcome-form').classList.add('hidden');
    document.getElementById('login-form').classList.remove('hidden');
    document.getElementById('register-form').classList.add('hidden');
    hideAuthError();
}

function showRegisterForm() {
    document.getElementById('welcome-form').classList.add('hidden');
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');
    hideAuthError();
}

function showAuthError(message) {
    const errorEl = document.getElementById('auth-error');
    errorEl.textContent = message;
    errorEl.classList.remove('hidden');
}

function hideAuthError() {
    document.getElementById('auth-error').classList.add('hidden');
}

async function handleLogin(event) {
    event.preventDefault();
    hideAuthError();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            isGuest = false;
            if (!currentUser.onboarding_completed) {
                showOnboarding();
            } else {
                showApp();
            }
        } else {
            showAuthError(data.error || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAuthError('Network error. Please try again.');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    hideAuthError();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value || null;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            isGuest = false;
            showOnboarding();
        } else {
            showAuthError(data.error || 'Registration failed');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAuthError('Network error. Please try again.');
    }
}

async function handleOnboarding(event) {
    event.preventDefault();
    
    const form = event.target;
    
    // Collect mediums from checkboxes
    const mediums = Array.from(form.querySelectorAll('input[name="mediums"]:checked'))
        .map(cb => cb.value);
    
    // Add custom mediums
    const customMediums = document.getElementById('custom-mediums').value
        .split(',')
        .map(s => s.trim())
        .filter(s => s);
    mediums.push(...customMediums);
    
    // Collect styles
    const styles = Array.from(form.querySelectorAll('input[name="styles"]:checked'))
        .map(cb => cb.value);
    
    const preferences = {
        favorite_mediums: mediums,
        favorite_styles: styles,
        skill_level: form.skill_level.value,
        session_length: form.session_length.value,
        budget_range: form.budget_range.value,
        goals: form.goals.value,
        pinterest_username: form.pinterest_username.value
    };
    
    // For guest mode, just save to local state and continue
    if (isGuest) {
        currentUser.preferences = preferences;
        showApp();
        return;
    }
    
    try {
        const response = await fetch('/api/auth/onboarding', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(preferences)
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            showApp();
        } else {
            console.error('Onboarding failed');
        }
    } catch (error) {
        console.error('Onboarding error:', error);
    }
}

async function skipOnboarding() {
    // For guest mode, just continue
    if (isGuest) {
        showApp();
        return;
    }
    
    try {
        const response = await fetch('/api/auth/onboarding', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ skip: true })
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            showApp();
        }
    } catch (error) {
        console.error('Skip onboarding error:', error);
    }
}

async function handleLogout() {
    if (!isGuest) {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                credentials: 'include'
            });
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
    
    currentUser = null;
    isGuest = false;
    currentConversationId = null;
    showAuth();
}

async function showPreferences() {
    // For guest users, use local state
    const user = isGuest ? (currentUser || {}) : null;
    
    if (!isGuest) {
        // Fetch current preferences for logged-in users
        try {
            const response = await fetch('/api/auth/me', { credentials: 'include' });
            if (!response.ok) return;
            
            const data = await response.json();
            showPreferencesModal(data.user);
        } catch (error) {
            console.error('Error loading preferences:', error);
        }
    } else {
        showPreferencesModal(currentUser);
    }
}

function showPreferencesModal(user) {
    const prefs = user.preferences || user || {};
    const mediums = prefs.favorite_mediums || [];
    const styles = prefs.favorite_styles || [];
    
    // List of standard mediums
    const standardMediums = [
        'watercolor', 'acrylic', 'oil', 'gouache', 'colored_pencil', 'graphite',
        'charcoal', 'ink', 'pastel', 'digital', 'mixed_media', 'crochet',
        'knitting', 'embroidery', 'sculpting', 'ceramics'
    ];
    
    // List of standard styles
    const standardStyles = [
        'realistic', 'impressionist', 'abstract', 'botanical',
        'portrait', 'landscape', 'minimalist', 'expressive'
    ];
    
    // Find custom mediums (not in standard list)
    const customMediums = mediums.filter(m => !standardMediums.includes(m));
    
    const modalContent = `
        <h2>⚙️ Update Preferences</h2>
        <form id="preferences-form" onsubmit="savePreferences(event)">
            <div class="form-group">
                <label>Mediums/Crafts</label>
                <div class="checkbox-grid modal-checkbox-grid">
                    ${standardMediums.map(m => `
                        <label><input type="checkbox" name="pref-mediums" value="${m}" ${mediums.includes(m) ? 'checked' : ''}> ${formatMediumName(m)}</label>
                    `).join('')}
                </div>
                <div class="custom-medium-input">
                    <label>Other:</label>
                    <input type="text" id="pref-custom-mediums" value="${customMediums.join(', ')}" placeholder="e.g., resin art, quilting...">
                    <small>Comma-separated list</small>
                </div>
            </div>
            
            <div class="form-group">
                <label>Styles</label>
                <div class="checkbox-grid modal-checkbox-grid">
                    ${standardStyles.map(s => `
                        <label><input type="checkbox" name="pref-styles" value="${s}" ${styles.includes(s) ? 'checked' : ''}> ${formatMediumName(s)}</label>
                    `).join('')}
                </div>
            </div>
            
            <div class="form-group">
                <label>Skill Level</label>
                <select id="pref-skill">
                    <option value="">Select one...</option>
                    <option value="beginner" ${prefs.skill_level === 'beginner' ? 'selected' : ''}>Beginner - Just starting out</option>
                    <option value="intermediate" ${prefs.skill_level === 'intermediate' ? 'selected' : ''}>Intermediate - Some experience</option>
                    <option value="advanced" ${prefs.skill_level === 'advanced' ? 'selected' : ''}>Advanced - Experienced artist</option>
                    <option value="professional" ${prefs.skill_level === 'professional' ? 'selected' : ''}>Professional - Make art for a living</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Session Length</label>
                <select id="pref-session">
                    <option value="">Select one...</option>
                    <option value="15-30min" ${prefs.session_length === '15-30min' ? 'selected' : ''}>Quick sketch (15-30 minutes)</option>
                    <option value="1-2hr" ${prefs.session_length === '1-2hr' ? 'selected' : ''}>Short session (1-2 hours)</option>
                    <option value="3-4hr" ${prefs.session_length === '3-4hr' ? 'selected' : ''}>Long session (3-4 hours)</option>
                    <option value="full_day" ${prefs.session_length === 'full_day' ? 'selected' : ''}>Full day immersion</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Monthly Supplies Budget</label>
                <select id="pref-budget">
                    <option value="">Select one...</option>
                    <option value="minimal" ${prefs.budget_range === 'minimal' ? 'selected' : ''}>Minimal ($0-25)</option>
                    <option value="modest" ${prefs.budget_range === 'modest' ? 'selected' : ''}>Modest ($25-75)</option>
                    <option value="comfortable" ${prefs.budget_range === 'comfortable' ? 'selected' : ''}>Comfortable ($75-200)</option>
                    <option value="generous" ${prefs.budget_range === 'generous' ? 'selected' : ''}>Generous ($200+)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Artistic Goals</label>
                <textarea id="pref-goals" rows="3" placeholder="E.g., improve my watercolor technique, build a portfolio...">${prefs.goals || ''}</textarea>
            </div>
            
            <div class="form-group">
                <label>Pinterest Board Link (optional)</label>
                <input type="text" id="pref-pinterest" value="${prefs.pinterest_username || ''}" placeholder="@yourusername">
            </div>
            
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Changes</button>
            </div>
        </form>
    `;
    
    openModal(modalContent);
}

function formatMediumName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

async function savePreferences(event) {
    event.preventDefault();
    
    // Collect mediums from checkboxes
    const mediums = Array.from(document.querySelectorAll('input[name="pref-mediums"]:checked'))
        .map(cb => cb.value);
    
    // Add custom mediums
    const customMediums = document.getElementById('pref-custom-mediums').value
        .split(',')
        .map(s => s.trim().toLowerCase())
        .filter(s => s);
    mediums.push(...customMediums);
    
    // Collect styles from checkboxes
    const styles = Array.from(document.querySelectorAll('input[name="pref-styles"]:checked'))
        .map(cb => cb.value);
    
    const preferences = {
        favorite_mediums: mediums,
        favorite_styles: styles,
        skill_level: document.getElementById('pref-skill').value,
        session_length: document.getElementById('pref-session').value,
        budget_range: document.getElementById('pref-budget').value,
        goals: document.getElementById('pref-goals').value,
        pinterest_username: document.getElementById('pref-pinterest').value
    };
    
    // For guest mode, save to local state only
    if (isGuest) {
        currentUser.preferences = preferences;
        currentUser.favorite_mediums = preferences.favorite_mediums;
        currentUser.favorite_styles = preferences.favorite_styles;
        currentUser.skill_level = preferences.skill_level;
        currentUser.session_length = preferences.session_length;
        currentUser.budget_range = preferences.budget_range;
        currentUser.goals = preferences.goals;
        currentUser.pinterest_username = preferences.pinterest_username;
        closeModal();
        return;
    }
    
    try {
        const response = await fetch('/api/auth/preferences', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(preferences)
        });
        
        if (response.ok) {
            const data = await response.json();
            currentUser = data.user;
            closeModal();
        }
    } catch (error) {
        console.error('Save preferences error:', error);
    }
}

// Conversation management
async function loadConversations() {
    try {
        const response = await fetch('/api/conversations', { credentials: 'include' });
        if (!response.ok) return;
        
        const data = await response.json();
        const list = document.getElementById('conversations-list');
        
        if (data.conversations.length === 0) {
            list.innerHTML = '<p class="empty-message">No conversations yet</p>';
            return;
        }
        
        list.innerHTML = data.conversations.map(conv => `
            <div class="list-item conversation-item ${conv.id === currentConversationId ? 'active' : ''}" 
                 data-conversation-id="${conv.id}">
                <div class="conversation-content" onclick="loadConversation(${conv.id})">
                    <span class="item-title">${escapeHtml(conv.title)}</span>
                    <span class="item-meta">${formatDate(conv.updated_at)}</span>
                </div>
                <button class="delete-conversation-btn" onclick="event.stopPropagation(); deleteConversation(${conv.id})" title="Delete conversation">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                </button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}

async function loadConversation(conversationId) {
    try {
        const response = await fetch(`/api/conversations/${conversationId}`, { credentials: 'include' });
        if (!response.ok) return;
        
        const data = await response.json();
        currentConversationId = conversationId;
        
        // Update conversation list to show active
        document.querySelectorAll('.conversation-item').forEach(el => {
            el.classList.remove('active');
            const elConvId = el.dataset.conversationId;
            if (elConvId && parseInt(elConvId) === conversationId) {
                el.classList.add('active');
            }
        });
        
        // Load messages into chat
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = data.conversation.messages.map(msg => {
            // Use formatMessageContent if available, otherwise basic escaping
            const content = typeof formatMessageContent === 'function' 
                ? formatMessageContent(msg.content)
                : `<p>${escapeHtml(msg.content)}</p>`;
            return `
                <div class="message ${msg.role}">
                    <div class="message-content">
                        ${content}
                    </div>
                </div>
            `;
        }).join('');
        
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

function startNewConversation() {
    currentConversationId = null;
    
    // Clear chat
    document.getElementById('chat-messages').innerHTML = `
        <div class="message assistant">
            <div class="message-content">
                <p>Starting a new conversation! How can I help you today?</p>
            </div>
        </div>
    `;
    
    // Update active state
    document.querySelectorAll('.conversation-item').forEach(el => {
        el.classList.remove('active');
    });
}

async function deleteConversation(conversationId) {
    if (!confirm('Delete this conversation?')) return;
    
    try {
        const response = await fetch(`/api/conversations/${conversationId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.ok) {
            // If we deleted the current conversation, start a new one
            if (currentConversationId === conversationId) {
                startNewConversation();
            }
            // Refresh the conversations list
            loadConversations();
        }
    } catch (error) {
        console.error('Error deleting conversation:', error);
    }
}

// Ideas management
async function loadIdeas() {
    try {
        const response = await fetch('/api/ideas', { credentials: 'include' });
        if (!response.ok) return;
        
        const data = await response.json();
        const list = document.getElementById('ideas-list');
        
        if (data.ideas.length === 0) {
            list.innerHTML = '<p class="empty-message">No saved ideas yet</p>';
            return;
        }
        
        list.innerHTML = data.ideas.slice(0, 5).map(idea => `
            <div class="list-item idea-item">
                <div class="item-content" onclick="viewIdea(${idea.id})">
                    <span class="item-title">${escapeHtml(idea.title)}</span>
                    ${idea.is_favorite ? '<span class="favorite-star">⭐</span>' : ''}
                </div>
                <button class="item-delete-btn" onclick="event.stopPropagation(); deleteIdea(${idea.id})" title="Delete idea">🗑️</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading ideas:', error);
    }
}

function openAddIdeaModal() {
    const modalContent = `
        <h2>💡 Save an Idea</h2>
        <form onsubmit="saveIdea(event)">
            <div class="form-group">
                <label>Title</label>
                <input type="text" id="idea-title" required placeholder="My brilliant idea...">
            </div>
            <div class="form-group">
                <label>Content</label>
                <textarea id="idea-content" rows="4" required placeholder="Describe your idea..."></textarea>
            </div>
            <div class="form-group">
                <label>Category</label>
                <select id="idea-category">
                    <option value="general">General</option>
                    <option value="project">Project Idea</option>
                    <option value="technique">Technique</option>
                    <option value="inspiration">Inspiration</option>
                    <option value="supply">Supply/Tool</option>
                </select>
            </div>
            <div class="form-group">
                <label>Tags (comma-separated)</label>
                <input type="text" id="idea-tags" placeholder="watercolor, landscape, ...">
            </div>
            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                <button type="submit" class="btn btn-primary">Save</button>
            </div>
        </form>
    `;
    openModal(modalContent);
}

async function saveIdea(event) {
    event.preventDefault();
    
    const idea = {
        title: document.getElementById('idea-title').value,
        content: document.getElementById('idea-content').value,
        category: document.getElementById('idea-category').value,
        tags: document.getElementById('idea-tags').value.split(',').map(s => s.trim()).filter(s => s)
    };
    
    try {
        const response = await fetch('/api/ideas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(idea)
        });
        
        if (response.ok) {
            closeModal();
            loadIdeas();
        }
    } catch (error) {
        console.error('Error saving idea:', error);
    }
}

async function viewIdea(ideaId) {
    try {
        const response = await fetch(`/api/ideas/${ideaId}`, { credentials: 'include' });
        if (!response.ok) return;
        
        const data = await response.json();
        const idea = data.idea;
        
        const modalContent = `
            <h2>${idea.is_favorite ? '⭐ ' : ''}${escapeHtml(idea.title)}</h2>
            <div class="idea-details">
                <p class="idea-category">Category: ${idea.category}</p>
                <div class="idea-content">${escapeHtml(idea.content)}</div>
                ${idea.tags && idea.tags.length ? `<p class="idea-tags">Tags: ${idea.tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join(' ')}</p>` : ''}
            </div>
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="toggleFavoriteIdea(${idea.id})">
                    ${idea.is_favorite ? 'Remove from Favorites' : 'Add to Favorites'}
                </button>
                <button class="btn btn-danger" onclick="deleteIdea(${idea.id})">Delete</button>
                <button class="btn btn-primary" onclick="closeModal()">Close</button>
            </div>
        `;
        openModal(modalContent);
    } catch (error) {
        console.error('Error viewing idea:', error);
    }
}

async function toggleFavoriteIdea(ideaId) {
    try {
        await fetch(`/api/ideas/${ideaId}/favorite`, {
            method: 'POST',
            credentials: 'include'
        });
        closeModal();
        loadIdeas();
    } catch (error) {
        console.error('Error toggling favorite:', error);
    }
}

async function deleteIdea(ideaId) {
    if (!confirm('Delete this idea?')) return;
    
    try {
        await fetch(`/api/ideas/${ideaId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        // Close modal if it's open
        const modal = document.getElementById('modal-overlay');
        if (modal && !modal.classList.contains('hidden')) {
            closeModal();
        }
        loadIdeas();
    } catch (error) {
        console.error('Error deleting idea:', error);
    }
}

// Helper functions
// View All functions
async function viewAllConversations() {
    try {
        const response = await fetch('/api/conversations', { credentials: 'include' });
        if (!response.ok) return;
        
        const data = await response.json();
        
        const conversationsHtml = data.conversations.length === 0 
            ? '<p class="empty-message">No conversations yet</p>'
            : data.conversations.map(conv => `
                <div class="view-all-item">
                    <div class="item-content" onclick="loadConversation(${conv.id}); closeModal();">
                        <span class="item-title">${escapeHtml(conv.title)}</span>
                        <span class="item-meta">${formatDate(conv.updated_at)}</span>
                    </div>
                    <button class="item-delete-btn" onclick="event.stopPropagation(); deleteConversation(${conv.id})" title="Delete">🗑️</button>
                </div>
            `).join('');
        
        openModal(`
            <div class="modal-header">
                <h3>💬 All Conversations (${data.conversations.length})</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="view-all-list">
                ${conversationsHtml}
            </div>
            <div class="form-actions">
                <button class="btn btn-primary" onclick="closeModal()">Close</button>
            </div>
        `);
    } catch (error) {
        console.error('Error loading all conversations:', error);
    }
}

async function viewAllIdeas() {
    try {
        const response = await fetch('/api/ideas', { credentials: 'include' });
        if (!response.ok) return;
        
        const data = await response.json();
        
        const ideasHtml = data.ideas.length === 0
            ? '<p class="empty-message">No saved ideas yet</p>'
            : data.ideas.map(idea => `
                <div class="view-all-item">
                    <div class="item-content" onclick="viewIdea(${idea.id})">
                        <span class="item-title">${escapeHtml(idea.title)}</span>
                        <span class="item-category">${idea.category || 'general'}</span>
                        ${idea.is_favorite ? '<span class="favorite-star">⭐</span>' : ''}
                    </div>
                    <button class="item-delete-btn" onclick="event.stopPropagation(); deleteIdea(${idea.id})" title="Delete">🗑️</button>
                </div>
            `).join('');
        
        openModal(`
            <div class="modal-header">
                <h3>💡 All Ideas (${data.ideas.length})</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="view-all-list">
                ${ideasHtml}
            </div>
            <div class="form-actions">
                <button class="btn btn-primary" onclick="openAddIdeaModal()">+ Add Idea</button>
                <button class="btn" onclick="closeModal()">Close</button>
            </div>
        `);
    } catch (error) {
        console.error('Error loading all ideas:', error);
    }
}

// Helper functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
}
