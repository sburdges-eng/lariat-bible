// Price Comparison JavaScript
// Handles price comparison, file upload, and Excel export/import

document.addEventListener('DOMContentLoaded', function() {
    initializePriceComparison();
    setupFileUploadHandlers();
});

function initializePriceComparison() {
    console.log('Price comparison initialized');
}

// ========================================
// File Upload Handling
// ========================================

function setupFileUploadHandlers() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    if (uploadArea && fileInput) {
        // Drag and drop
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        uploadArea.addEventListener('drop', handleDrop);
    }
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFileUpload(event) {
    const files = event.target.files;
    handleFiles(files);
}

async function handleFiles(files) {
    const formData = new FormData();

    Array.from(files).forEach((file, index) => {
        formData.append('file', file);
    });

    try {
        LariatBible.showLoading();

        const response = await fetch('/api/import/price-list', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        LariatBible.hideLoading();

        if (result.success) {
            LariatBible.showNotification(result.message, 'success');
            displayUploadResults(result);
        } else {
            LariatBible.showNotification(result.error || 'Upload failed', 'error');
        }
    } catch (error) {
        LariatBible.hideLoading();
        LariatBible.showNotification('Upload error: ' + error.message, 'error');
    }
}

function displayUploadResults(result) {
    const statusDiv = document.getElementById('uploadStatus');
    if (!statusDiv) return;

    let html = `
        <div style="margin-top: 1rem; padding: 1rem; background: #f7f8fc; border-radius: 8px;">
            <h4 style="color: #43e97b; margin-bottom: 0.5rem;">✓ Upload Successful</h4>
            <p><strong>${result.message}</strong></p>
            <p style="font-size: 0.9rem; color: #718096;">Columns detected: ${result.columns.join(', ')}</p>
        </div>
    `;

    statusDiv.innerHTML = html;
}

// ========================================
// Export Functions
// ========================================

function exportPriceComparison() {
    LariatBible.downloadFile('/api/export/price-comparison', `price_comparison_${Date.now()}.xlsx`);
}

function exportTopSavings() {
    LariatBible.downloadFile('/api/export/savings-opportunities', `top_savings_${Date.now()}.xlsx`);
}

function exportByCategory() {
    LariatBible.downloadFile('/api/export/price-comparison', `category_analysis_${Date.now()}.xlsx`);
}

function exportCustomReport() {
    // Implement custom report options
    LariatBible.showNotification('Custom report builder coming soon', 'info');
}

function exportResults() {
    exportPriceComparison();
}

// ========================================
// Product Search and Comparison
// ========================================

function searchProducts() {
    const searchValue = document.getElementById('productSearch').value;
    // Implement product search
    console.log('Searching for:', searchValue);
}

function compareProduct() {
    const searchValue = document.getElementById('productSearch').value;
    if (!searchValue) {
        LariatBible.showNotification('Please enter a product name or code', 'error');
        return;
    }

    // Implement product comparison
    LariatBible.showNotification('Comparing product: ' + searchValue, 'info');
}

function clearResults() {
    const resultsTable = document.getElementById('resultsTable');
    if (resultsTable) {
        resultsTable.innerHTML = '';
    }
    LariatBible.showNotification('Results cleared', 'info');
}

// ========================================
// Template Downloads
// ========================================

function downloadTemplate(vendor) {
    let templateType = 'price_list';

    fetch(`/api/template/${templateType}`)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${vendor}_price_list_template.xlsx`;
            a.click();
            window.URL.revokeObjectURL(url);
            LariatBible.showNotification('Template downloaded', 'success');
        })
        .catch(error => {
            console.error('Template download error:', error);
            LariatBible.showNotification('Failed to download template', 'error');
        });
}
