/**
 * The Lariat Bible - Main JavaScript
 * Interactive functionality for the dashboard
 */

// API Configuration
const API_BASE_URL = window.location.origin;

// ==================== Utility Functions ====================

/**
 * Fetch data from API endpoint
 * @param {string} endpoint - API endpoint path
 * @returns {Promise<Object>} Response data
 */
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Format currency
 * @param {number} amount - Dollar amount
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Format number with commas
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of notification (success, error, info, warning)
 */
function showToast(message, type = 'info') {
    // Simple console log for now - can be enhanced with a toast library
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// ==================== Dashboard Data Loading ====================

/**
 * Load dashboard statistics
 */
async function loadDashboardStats() {
    try {
        const data = await fetchAPI('/');

        // Update metrics
        if (data.metrics) {
            const monthlyRevenue = data.metrics.monthly_catering_revenue + data.metrics.monthly_restaurant_revenue;
            document.getElementById('monthlyRevenue').textContent = formatCurrency(monthlyRevenue);
            document.getElementById('potentialSavings').textContent = formatCurrency(data.metrics.potential_annual_savings);
        }

        // Simulate some dynamic data
        document.getElementById('upcomingEvents').textContent = Math.floor(Math.random() * 10) + 5;
        document.getElementById('lowStockItems').textContent = Math.floor(Math.random() * 20) + 5;

        console.log('Dashboard stats loaded successfully');
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        showToast('Failed to load dashboard statistics', 'error');
    }
}

/**
 * Load system modules status
 */
async function loadModulesStatus() {
    try {
        const modules = await fetchAPI('/api/modules');
        const container = document.getElementById('modulesStatus');

        if (!modules || modules.length === 0) {
            container.innerHTML = '<p class="text-secondary">No modules available</p>';
            return;
        }

        // Create module list HTML
        const html = modules.map(module => {
            const statusClass = module.status === 'active' ? 'success' :
                               module.status === 'development' ? 'warning' : 'neutral';
            const statusIcon = module.status === 'active' ? 'check-circle' :
                              module.status === 'development' ? 'code' : 'clock';

            return `
                <div class="activity-item">
                    <div class="activity-icon ${statusClass === 'success' ? 'green' : statusClass === 'warning' ? 'orange' : 'blue'}">
                        <i class="fas fa-${statusIcon}"></i>
                    </div>
                    <div class="activity-content">
                        <p><strong>${module.name}</strong></p>
                        <span class="activity-time">${module.description}</span>
                    </div>
                    <span class="stat-change ${statusClass}">
                        ${module.status}
                    </span>
                </div>
            `;
        }).join('');

        container.innerHTML = `<div class="activity-list">${html}</div>`;
        console.log('Modules status loaded successfully');
    } catch (error) {
        console.error('Error loading modules:', error);
        const container = document.getElementById('modulesStatus');
        container.innerHTML = '<p class="text-secondary">Failed to load modules</p>';
        showToast('Failed to load system modules', 'error');
    }
}

/**
 * Load vendor comparison data
 */
async function loadVendorComparison() {
    try {
        const data = await fetchAPI('/api/vendor/comparison');

        if (data.savings) {
            const savingsElement = document.querySelector('.savings-highlight strong');
            if (savingsElement) {
                savingsElement.textContent = formatCurrency(data.savings.monthly) + '/month';
            }
        }

        console.log('Vendor comparison loaded successfully');
    } catch (error) {
        console.error('Error loading vendor comparison:', error);
        // Don't show error toast for this as it's not critical
    }
}

/**
 * Check API health
 */
async function checkAPIHealth() {
    try {
        const health = await fetchAPI('/api/health');
        console.log('API Health Check:', health);

        if (health.status === 'healthy') {
            console.log('✅ System is healthy');
        }
    } catch (error) {
        console.error('❌ API health check failed:', error);
        showToast('Warning: API health check failed', 'warning');
    }
}

// ==================== UI Interactions ====================

/**
 * Handle navigation clicks
 */
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            // Remove active class from all items
            navItems.forEach(nav => nav.classList.remove('active'));

            // Add active class to clicked item
            item.classList.add('active');

            // Get the href (page section)
            const href = item.getAttribute('href');
            console.log(`Navigating to: ${href}`);

            showToast(`Navigating to ${item.textContent.trim()}`, 'info');
        });
    });
}

/**
 * Handle quick action buttons
 */
function initQuickActions() {
    const quickActions = document.querySelectorAll('.quick-action-btn');

    quickActions.forEach(btn => {
        btn.addEventListener('click', () => {
            const actionName = btn.querySelector('span').textContent;
            console.log(`Quick action triggered: ${actionName}`);
            showToast(`${actionName} - Feature coming soon!`, 'info');
        });
    });
}

/**
 * Handle notification button
 */
function initNotifications() {
    const notificationBtn = document.getElementById('notificationBtn');

    if (notificationBtn) {
        notificationBtn.addEventListener('click', () => {
            console.log('Notifications clicked');
            showToast('3 new notifications', 'info');
        });
    }
}

/**
 * Handle settings button
 */
function initSettings() {
    const settingsBtn = document.getElementById('settingsBtn');

    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            console.log('Settings clicked');
            showToast('Settings panel coming soon!', 'info');
        });
    }
}

/**
 * Animate stat cards on load
 */
function animateStats() {
    const statCards = document.querySelectorAll('.stat-card');

    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

/**
 * Update timestamp periodically
 */
function updateTimestamp() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });

    // Could be used to display current time in the dashboard
    console.log(`Current time: ${timeString}`);
}

// ==================== Auto-refresh ====================

/**
 * Set up periodic data refresh
 */
function initAutoRefresh() {
    // Refresh dashboard stats every 5 minutes
    setInterval(loadDashboardStats, 5 * 60 * 1000);

    // Refresh vendor comparison every 10 minutes
    setInterval(loadVendorComparison, 10 * 60 * 1000);

    // Update timestamp every minute
    setInterval(updateTimestamp, 60 * 1000);

    console.log('Auto-refresh enabled');
}

// ==================== Initialization ====================

/**
 * Initialize the dashboard
 */
async function initDashboard() {
    console.log('🚀 Initializing The Lariat Bible Dashboard...');

    try {
        // Check API health first
        await checkAPIHealth();

        // Load all data in parallel
        await Promise.all([
            loadDashboardStats(),
            loadModulesStatus(),
            loadVendorComparison()
        ]);

        // Initialize UI components
        initNavigation();
        initQuickActions();
        initNotifications();
        initSettings();

        // Animate stats
        animateStats();

        // Set up auto-refresh
        initAutoRefresh();

        console.log('✅ Dashboard initialized successfully');
        showToast('Dashboard loaded successfully', 'success');

    } catch (error) {
        console.error('❌ Dashboard initialization failed:', error);
        showToast('Failed to initialize dashboard', 'error');
    }
}

// ==================== Event Listeners ====================

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}

// Handle window resize for responsive behavior
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        console.log('Window resized');
        // Could trigger responsive layout adjustments here
    }, 250);
});

// Handle visibility change to pause/resume updates
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Page hidden - could pause updates');
    } else {
        console.log('Page visible - resuming updates');
        loadDashboardStats();
    }
});

// ==================== Export for external use ====================
window.LariatBible = {
    loadDashboardStats,
    loadModulesStatus,
    loadVendorComparison,
    showToast,
    formatCurrency,
    formatNumber
};

console.log('📚 The Lariat Bible JavaScript loaded');
