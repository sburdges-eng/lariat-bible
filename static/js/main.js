// Main JavaScript - The Lariat Bible
// Common functionality across all pages

// ========================================
// Global Configuration
// ========================================

const API_BASE_URL = window.location.origin;

// ========================================
// Utility Functions
// ========================================

function formatCurrency(value) {
    return '$' + parseFloat(value).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
}

function formatPercent(value) {
    return parseFloat(value).toFixed(1) + '%';
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#43e97b' : type === 'error' ? '#f5576c' : '#4facfe'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showLoading() {
    const loader = document.createElement('div');
    loader.id = 'globalLoader';
    loader.innerHTML = `
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        ">
            <div class="loading"></div>
        </div>
    `;
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('globalLoader');
    if (loader) loader.remove();
}

// ========================================
// API Helper Functions
// ========================================

async function apiGet(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API GET error:', error);
        showNotification('Failed to fetch data', 'error');
        throw error;
    }
}

async function apiPost(endpoint, data) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API POST error:', error);
        showNotification('Failed to submit data', 'error');
        throw error;
    }
}

async function downloadFile(endpoint, filename) {
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || `download-${Date.now()}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        hideLoading();
        showNotification('File downloaded successfully', 'success');
    } catch (error) {
        hideLoading();
        console.error('Download error:', error);
        showNotification('Failed to download file', 'error');
        throw error;
    }
}

// ========================================
// File Upload Handling
// ========================================

function setupFileUpload(inputId, callback) {
    const input = document.getElementById(inputId);
    if (!input) return;

    input.addEventListener('change', async (event) => {
        const files = event.target.files;
        if (files.length === 0) return;

        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }

        try {
            showLoading();
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Upload failed');

            const result = await response.json();
            hideLoading();
            showNotification('Files uploaded successfully', 'success');

            if (callback) callback(result);
        } catch (error) {
            hideLoading();
            console.error('Upload error:', error);
            showNotification('Failed to upload files', 'error');
        }
    });
}

// ========================================
// Drag and Drop File Upload
// ========================================

function setupDragAndDrop(areaId, callback) {
    const area = document.getElementById(areaId);
    if (!area) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        area.addEventListener(eventName, () => {
            area.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, () => {
            area.classList.remove('drag-over');
        });
    });

    area.addEventListener('drop', async (e) => {
        const files = e.dataTransfer.files;
        if (files.length === 0) return;

        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }

        try {
            showLoading();
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Upload failed');

            const result = await response.json();
            hideLoading();
            showNotification('Files uploaded successfully', 'success');

            if (callback) callback(result);
        } catch (error) {
            hideLoading();
            console.error('Upload error:', error);
            showNotification('Failed to upload files', 'error');
        }
    });
}

// ========================================
// Data Table Generator
// ========================================

function createDataTable(containerId, data, columns) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = `
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
    `;

    columns.forEach(col => {
        html += `<th style="padding: 1rem; text-align: ${col.align || 'left'}; font-weight: 600;">${col.label}</th>`;
    });

    html += `
                    </tr>
                </thead>
                <tbody>
    `;

    data.forEach((row, index) => {
        const rowStyle = index % 2 === 0 ? 'background: #f7f8fc;' : 'background: white;';
        html += `<tr style="${rowStyle}">`;

        columns.forEach(col => {
            let value = row[col.field];
            if (col.formatter) value = col.formatter(value, row);
            html += `<td style="padding: 1rem; text-align: ${col.align || 'left'};">${value}</td>`;
        });

        html += `</tr>`;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}

// ========================================
// Local Storage Helper
// ========================================

const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(`lariat_${key}`, JSON.stringify(value));
        } catch (error) {
            console.error('Storage set error:', error);
        }
    },

    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(`lariat_${key}`);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Storage get error:', error);
            return defaultValue;
        }
    },

    remove: (key) => {
        try {
            localStorage.removeItem(`lariat_${key}`);
        } catch (error) {
            console.error('Storage remove error:', error);
        }
    },

    clear: () => {
        try {
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith('lariat_')) {
                    localStorage.removeItem(key);
                }
            });
        } catch (error) {
            console.error('Storage clear error:', error);
        }
    }
};

// ========================================
// Auto-save Form Data
// ========================================

function setupAutoSave(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    const inputs = form.querySelectorAll('input, select, textarea');

    inputs.forEach(input => {
        const savedValue = storage.get(`form_${formId}_${input.id}`);
        if (savedValue && input.value === '') {
            input.value = savedValue;
        }

        input.addEventListener('change', () => {
            storage.set(`form_${formId}_${input.id}`, input.value);
        });
    });
}

// ========================================
// Debounce Function
// ========================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ========================================
// Export to CSV
// ========================================

function exportToCSV(data, filename) {
    if (!data || !data.length) {
        showNotification('No data to export', 'error');
        return;
    }

    const headers = Object.keys(data[0]);
    const csv = [
        headers.join(','),
        ...data.map(row => headers.map(field => JSON.stringify(row[field] || '')).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || `export-${Date.now()}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);

    showNotification('CSV exported successfully', 'success');
}

// ========================================
// Search/Filter Helpers
// ========================================

function filterTable(tableId, searchValue, columnIndex = null) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const rows = table.getElementsByTagName('tr');
    searchValue = searchValue.toLowerCase();

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        let text = '';

        if (columnIndex !== null) {
            const cell = row.getElementsByTagName('td')[columnIndex];
            text = cell ? cell.textContent || cell.innerText : '';
        } else {
            text = row.textContent || row.innerText;
        }

        if (text.toLowerCase().indexOf(searchValue) > -1) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    }
}

// ========================================
// Initialize Common Features
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Highlight active nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.background = 'rgba(255, 255, 255, 0.2)';
        }
    });

    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// ========================================
// Global Error Handler
// ========================================

window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
});

// ========================================
// Export Functions
// ========================================

window.LariatBible = {
    formatCurrency,
    formatPercent,
    showNotification,
    showLoading,
    hideLoading,
    apiGet,
    apiPost,
    downloadFile,
    createDataTable,
    storage,
    exportToCSV,
    filterTable,
    debounce,
};
