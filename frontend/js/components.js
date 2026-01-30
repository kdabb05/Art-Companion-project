/**
 * Art Studio Companion - Additional UI Components
 */

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Escape closes modals
    if (e.key === 'Escape') {
        closeModal();
    }
    
    // Ctrl/Cmd + K focuses chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('chat-input').focus();
    }
});

// Touch-friendly sidebar toggle for mobile
function toggleSidebar(side) {
    const sidebar = document.querySelector(side === 'left' ? '.supplies-sidebar' : '.right-sidebar');
    sidebar.classList.toggle('visible');
}

// Notification helper
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style it
    Object.assign(notification.style, {
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        padding: '12px 20px',
        borderRadius: '8px',
        backgroundColor: type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : '#6366f1',
        color: 'white',
        zIndex: '2000',
        animation: 'slideIn 0.3s ease',
    });
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @media (max-width: 1024px) {
        .supplies-sidebar,
        .right-sidebar {
            position: fixed;
            top: 0;
            bottom: 0;
            width: 300px;
            z-index: 100;
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        .right-sidebar {
            right: 0;
            left: auto;
            transform: translateX(100%);
        }
        
        .supplies-sidebar.visible,
        .right-sidebar.visible {
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style);

// Export functions
window.showNotification = showNotification;
window.toggleSidebar = toggleSidebar;
