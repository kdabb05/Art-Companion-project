/**
 * Art Studio Companion - Chat functionality
 */

// Chat state
let isWaitingForResponse = false;

// Initialize chat
document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    
    chatForm.addEventListener('submit', handleChatSubmit);
});

async function handleChatSubmit(event) {
    event.preventDefault();
    
    if (isWaitingForResponse) return;
    
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Clear input
    input.value = '';
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Send to API
    await sendChatMessage(message);
}

function addMessage(content, role) {
    const container = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Handle markdown-like formatting
    const formattedContent = formatMessageContent(content);
    contentDiv.innerHTML = formattedContent;
    
    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function addLoadingMessage() {
    const container = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.id = 'loading-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<div class="loading"></div> Thinking...';
    
    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function removeLoadingMessage() {
    const loading = document.getElementById('loading-message');
    if (loading) {
        loading.remove();
    }
}

async function sendChatMessage(message) {
    isWaitingForResponse = true;
    addLoadingMessage();
    
    try {
        const payload = { message };
        
        // Include conversation_id if we're in an existing conversation
        if (typeof currentConversationId !== 'undefined' && currentConversationId) {
            payload.conversation_id = currentConversationId;
        }
        
        // Include guest mode info
        if (typeof isGuest !== 'undefined' && isGuest) {
            payload.is_guest = true;
            // Include preferences for guest context
            if (typeof currentUser !== 'undefined' && currentUser && currentUser.preferences) {
                payload.preferences = currentUser.preferences;
            } else if (typeof currentUser !== 'undefined' && currentUser) {
                // Preferences might be stored directly on currentUser for guests
                payload.preferences = {
                    favorite_mediums: currentUser.favorite_mediums || [],
                    favorite_styles: currentUser.favorite_styles || [],
                    skill_level: currentUser.skill_level,
                    session_length: currentUser.session_length,
                    budget_range: currentUser.budget_range,
                    goals: currentUser.goals
                };
            }
        }
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(payload),
        });
        
        const data = await response.json();
        
        removeLoadingMessage();
        
        if (response.status === 401 && !isGuest) {
            // Not authenticated and not in guest mode
            if (typeof showAuth === 'function') {
                showAuth();
            }
            return;
        }
        
        if (data.success) {
            addMessage(data.response, 'assistant');
            
            // Update current conversation ID (only for logged-in users)
            if (data.conversation_id && !isGuest) {
                if (typeof currentConversationId !== 'undefined') {
                    currentConversationId = data.conversation_id;
                }
                // Refresh conversations list
                if (typeof loadConversations === 'function') {
                    loadConversations();
                }
            }
            
            // If tools were called, refresh relevant data
            if (data.tool_calls && data.tool_calls.length > 0) {
                refreshDataAfterToolCalls(data.tool_calls);
            }
        } else {
            addMessage(data.response || data.error || 'Sorry, something went wrong. Please try again.', 'assistant');
        }
    } catch (error) {
        console.error('Chat error:', error);
        removeLoadingMessage();
        addMessage('Sorry, I\'m having trouble connecting. Please try again.', 'assistant');
    }
    
    isWaitingForResponse = false;
}

function refreshDataAfterToolCalls(toolCalls) {
    // Refresh relevant panels based on which tools were called
    for (const call of toolCalls) {
        switch (call.tool) {
            case 'inventory_tool':
                loadSupplies();
                break;
            case 'project_tool':
                loadProjects();
                break;
            case 'portfolio_tool':
                loadPortfolio();
                break;
        }
    }
}

function formatMessageContent(content) {
    if (!content) return '';
    
    // Escape HTML first
    let formatted = escapeHtml(content);
    
    // Convert markdown links [text](url) to clickable links (before plain URL conversion)
    formatted = formatted.replace(
        /\[([^\]]+)\]\((https?:\/\/[^\s\)]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    // Convert plain URLs to clickable links (only if not already in a link)
    // Match URLs starting with http:// or https:// that aren't already in href=""
    formatted = formatted.replace(
        /(?<!href=")(https?:\/\/[^\s<>"']+)(?!")/g,
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    // Convert line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Bold text: **text**
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italic text: *text*
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Code: `text`
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Convert numbered lists (1. item)
    formatted = formatted.replace(/^(\d+)\.\s+/gm, '$1. ');
    
    return `<p>${formatted}</p>`;
}

// Quick action buttons can trigger chat messages
function askAgent(message) {
    document.getElementById('chat-input').value = message;
    document.getElementById('chat-form').dispatchEvent(new Event('submit'));
}

// Expose for use in quick actions
window.askAgent = askAgent;
