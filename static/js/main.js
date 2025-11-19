/**
 * The Lariat Bible - Main JavaScript
 * Modern interactive features
 */

// ========================================
// Toast Notifications System
// ========================================

class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container');
    }

    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 1rem;">
                <i class="fas ${icons[type]}" style="font-size: 1.5rem;"></i>
                <div style="flex: 1;">${message}</div>
                <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: inherit; cursor: pointer; font-size: 1.25rem;">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        this.container.appendChild(toast);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-out forwards';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }

        return toast;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Global toast instance
const toast = new ToastManager();

// ========================================
// Navigation Active State
// ========================================

function updateActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// ========================================
// Animate on Scroll
// ========================================

function animateOnScroll() {
    const elements = document.querySelectorAll('.stat-card, .card');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    elements.forEach(el => observer.observe(el));
}

// ========================================
// Number Animation (Count Up Effect)
// ========================================

function animateNumber(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 16); // 60fps
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }

        // Format based on content
        if (element.textContent.includes('$')) {
            element.textContent = '$' + Math.floor(current).toLocaleString();
        } else if (element.textContent.includes('%')) {
            element.textContent = Math.floor(current) + '%';
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

// ========================================
// Dashboard Data Loading
// ========================================

async function loadDashboardMetrics() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            console.log('✅ System healthy:', data.restaurant);
        }
    } catch (error) {
        console.error('Error loading dashboard metrics:', error);
        toast.error('Failed to load dashboard data');
    }
}

// ========================================
// Refresh Data Function
// ========================================

async function refreshData() {
    const btn = event.currentTarget;
    const icon = btn.querySelector('i');

    icon.style.animation = 'spin 1s linear infinite';

    try {
        await loadDashboardMetrics();
        toast.success('Data refreshed successfully!');
    } catch (error) {
        toast.error('Failed to refresh data');
    } finally {
        icon.style.animation = '';
    }
}

// ========================================
// Search Functionality
// ========================================

function initSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const query = e.target.value.toLowerCase();
            performSearch(query);
        }, 300);
    });
}

function performSearch(query) {
    if (!query) {
        console.log('Search cleared');
        return;
    }

    console.log('Searching for:', query);
    // Implement actual search logic here
}

// ========================================
// Dark/Light Mode Toggle (Future Feature)
// ========================================

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    toast.info(`Switched to ${newTheme} mode`);
}

// ========================================
// Keyboard Shortcuts
// ========================================

function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) searchInput.focus();
        }

        // Ctrl/Cmd + R for refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            refreshData();
        }
    });
}

// ========================================
// Notification Button Handler
// ========================================

function initNotifications() {
    const notificationBtn = document.getElementById('notificationBtn');
    if (!notificationBtn) return;

    notificationBtn.addEventListener('click', () => {
        toast.info('You have 3 new notifications');
        // Future: Open notifications panel
    });
}

// ========================================
// Settings Button Handler
// ========================================

function initSettings() {
    const settingsBtn = document.getElementById('settingsBtn');
    if (!settingsBtn) return;

    settingsBtn.addEventListener('click', () => {
        toast.info('Settings panel coming soon!');
        // Future: Open settings modal
    });
}

// ========================================
// Real-time Clock (Optional)
// ========================================

function updateClock() {
    const clockElement = document.getElementById('currentTime');
    if (!clockElement) return;

    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    clockElement.textContent = timeString;
}

// ========================================
// Auto-refresh Data (Optional)
// ========================================

function startAutoRefresh(interval = 60000) {
    // Refresh every minute by default
    setInterval(() => {
        loadDashboardMetrics();
    }, interval);
}

// ========================================
// Form Validation Helper
// ========================================

function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });

    return isValid;
}

// ========================================
// API Helper Functions
// ========================================

async function apiGet(endpoint) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API GET Error:', error);
        throw error;
    }
}

async function apiPost(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API POST Error:', error);
        throw error;
    }
}

// ========================================
// Loading State Manager
// ========================================

class LoadingManager {
    show(element, text = 'Loading...') {
        const spinner = document.createElement('div');
        spinner.className = 'loading-overlay';
        spinner.innerHTML = `
            <div style="text-align: center;">
                <i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: var(--primary);"></i>
                <p style="margin-top: 1rem; color: var(--text-secondary);">${text}</p>
            </div>
        `;
        element.style.position = 'relative';
        element.appendChild(spinner);
    }

    hide(element) {
        const spinner = element.querySelector('.loading-overlay');
        if (spinner) spinner.remove();
    }
}

const loading = new LoadingManager();

// ========================================
// Initialize Everything on Page Load
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🤠 The Lariat Bible - Initializing...');

    // Initialize core features
    updateActiveNavLink();
    animateOnScroll();
    initSearch();
    initKeyboardShortcuts();
    initNotifications();
    initSettings();
    loadDashboardMetrics();

    // Animate stat numbers on load
    const statValues = document.querySelectorAll('.stat-value');
    statValues.forEach((stat, index) => {
        setTimeout(() => {
            const text = stat.textContent;
            const number = parseInt(text.replace(/[^0-9]/g, ''));
            if (number) {
                stat.textContent = text.replace(number, '0');
                animateNumber(stat, number);
            }
        }, index * 100);
    });

    // Optional: Start auto-refresh
    // startAutoRefresh(60000); // Refresh every minute

    console.log('✅ Initialization complete!');

    // Welcome message
    setTimeout(() => {
        toast.success('Welcome to The Lariat Bible!', 4000);
    }, 500);
});

// ========================================
// Export for use in other scripts
// ========================================

window.LariatBible = {
    toast,
    loading,
    apiGet,
    apiPost,
    validateForm,
    refreshData
};

// ========================================
// CSS for Loading Overlay
// ========================================

const style = document.createElement('style');
style.textContent = `
    .loading-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(15, 23, 42, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
        border-radius: inherit;
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    @keyframes slideOut {
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    .error {
        border-color: var(--danger) !important;
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
    }
`;
document.head.appendChild(style);
