// Order Guides JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeOrderGuides();
});

function initializeOrderGuides() {
    console.log('Order guides initialized');
}

function importOrderGuide() {
    document.getElementById('guideFileInput').click();
}

function exportOrderGuide() {
    const vendor = document.getElementById('vendorSelect')?.value || 'shamrock';
    LariatBible.downloadFile('/api/export/order-guide', `order_guide_${vendor}_${Date.now()}.xlsx`);
}

function handleGuideUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    LariatBible.showLoading();

    fetch('/api/import/order-guide', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        LariatBible.hideLoading();
        if (result.success) {
            LariatBible.showNotification(result.message, 'success');
        } else {
            LariatBible.showNotification(result.error || 'Import failed', 'error');
        }
    })
    .catch(error => {
        LariatBible.hideLoading();
        LariatBible.showNotification('Import error: ' + error.message, 'error');
    });
}

function performExport() {
    exportOrderGuide();
}

function viewGuide(vendor) {
    console.log('Viewing guide for:', vendor);
    LariatBible.showNotification(`Opening ${vendor} order guide`, 'info');
}

function downloadGuide(vendor) {
    LariatBible.downloadFile('/api/export/order-guide', `${vendor}_order_guide_${Date.now()}.xlsx`);
}

function editGuide(vendor) {
    console.log('Editing guide for:', vendor);
    LariatBible.showNotification('Guide editor coming soon', 'info');
}

function compareGuides() {
    const guide1 = document.getElementById('compareGuide1').value;
    const guide2 = document.getElementById('compareGuide2').value;
    console.log(`Comparing ${guide1} with ${guide2}`);
    LariatBible.showNotification('Comparison in progress...', 'info');
}

function closeViewer() {
    const viewer = document.getElementById('guideViewer');
    if (viewer) {
        viewer.style.display = 'none';
    }
}
