/**
 * The Lariat Bible - Advanced Interactive Features
 * Drag-drop upload, PDF generation, and inventory alerts
 */

// ==================== Drag-and-Drop Invoice Upload ====================

class InvoiceUploader {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.files = [];
        this.uploadedInvoices = [];
        this.init();
    }

    init() {
        if (!this.container) return;
        this.render();
        this.attachEvents();
    }

    render() {
        const html = `
            <div class="invoice-uploader">
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <h3>Drag & Drop Invoices Here</h3>
                    <p>or click to browse files</p>
                    <p class="upload-hint">Supports PDF, JPG, PNG (Max 16MB)</p>
                    <input type="file" id="fileInput" multiple accept=".pdf,.jpg,.jpeg,.png" hidden>
                    <button class="btn btn-primary" id="browseBtn">
                        <i class="fas fa-folder-open"></i> Browse Files
                    </button>
                </div>

                <div class="upload-queue" id="uploadQueue" style="display: none;">
                    <h4><i class="fas fa-list"></i> Upload Queue</h4>
                    <div id="queueList"></div>
                </div>

                <div class="uploaded-invoices" id="uploadedList">
                    <h4><i class="fas fa-file-invoice"></i> Recent Uploads</h4>
                    <div id="invoicesList">
                        ${this.uploadedInvoices.length === 0 ?
                            '<p class="no-invoices">No invoices uploaded yet</p>' :
                            this.uploadedInvoices.map(inv => this.renderInvoice(inv)).join('')
                        }
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
    }

    attachEvents() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseBtn');

        if (!uploadArea || !fileInput) return;

        // Drag and drop events
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');

            const files = Array.from(e.dataTransfer.files);
            this.handleFiles(files);
        });

        // Browse button
        browseBtn.addEventListener('click', () => fileInput.click());

        // File input change
        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFiles(files);
        });
    }

    handleFiles(files) {
        const validFiles = files.filter(file => this.validateFile(file));

        if (validFiles.length === 0) {
            notifications.show('No valid files selected', 'error');
            return;
        }

        this.files = validFiles;
        this.showQueue();
        this.processFiles();
    }

    validateFile(file) {
        const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
        const maxSize = 16 * 1024 * 1024; // 16MB

        if (!validTypes.includes(file.type)) {
            notifications.show(`${file.name}: Invalid file type`, 'error');
            return false;
        }

        if (file.size > maxSize) {
            notifications.show(`${file.name}: File too large (max 16MB)`, 'error');
            return false;
        }

        return true;
    }

    showQueue() {
        const queue = document.getElementById('uploadQueue');
        const queueList = document.getElementById('queueList');

        if (!queue || !queueList) return;

        queue.style.display = 'block';
        queueList.innerHTML = this.files.map((file, idx) => `
            <div class="queue-item" id="queueItem${idx}">
                <div class="queue-info">
                    <i class="fas fa-file-${this.getFileIcon(file.type)}"></i>
                    <div>
                        <div class="queue-name">${file.name}</div>
                        <div class="queue-size">${this.formatFileSize(file.size)}</div>
                    </div>
                </div>
                <div class="queue-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress${idx}" style="width: 0%"></div>
                    </div>
                    <span class="progress-text" id="progressText${idx}">0%</span>
                </div>
            </div>
        `).join('');
    }

    async processFiles() {
        for (let i = 0; i < this.files.length; i++) {
            await this.uploadFile(this.files[i], i);
        }

        notifications.show(`${this.files.length} invoice(s) processed successfully`, 'success');
        this.files = [];

        // Hide queue after a delay
        setTimeout(() => {
            const queue = document.getElementById('uploadQueue');
            if (queue) queue.style.display = 'none';
        }, 2000);
    }

    async uploadFile(file, index) {
        // Simulate upload progress
        const progressBar = document.getElementById(`progress${index}`);
        const progressText = document.getElementById(`progressText${index}`);

        for (let progress = 0; progress <= 100; progress += 10) {
            await new Promise(resolve => setTimeout(resolve, 100));

            if (progressBar) progressBar.style.width = `${progress}%`;
            if (progressText) progressText.textContent = `${progress}%`;
        }

        // Simulate OCR processing
        await this.simulateOCR(file);

        // Add to uploaded list
        const invoice = {
            id: Date.now() + index,
            name: file.name,
            size: file.size,
            type: file.type,
            uploadedAt: new Date(),
            vendor: this.extractVendor(file.name),
            amount: this.generateRandomAmount(),
            status: 'processed'
        };

        this.uploadedInvoices.unshift(invoice);
        this.updateUploadedList();
    }

    async simulateOCR(file) {
        // Simulate OCR processing delay
        await new Promise(resolve => setTimeout(resolve, 500));
        console.log(`OCR processing: ${file.name}`);
    }

    extractVendor(filename) {
        const vendors = ['Shamrock Foods', 'SYSCO', 'US Foods', 'Restaurant Depot'];
        return vendors[Math.floor(Math.random() * vendors.length)];
    }

    generateRandomAmount() {
        return (Math.random() * 5000 + 500).toFixed(2);
    }

    updateUploadedList() {
        const invoicesList = document.getElementById('invoicesList');
        if (!invoicesList) return;

        invoicesList.innerHTML = this.uploadedInvoices.slice(0, 10).map(inv => this.renderInvoice(inv)).join('');
    }

    renderInvoice(invoice) {
        const date = new Date(invoice.uploadedAt);
        return `
            <div class="invoice-item">
                <div class="invoice-icon">
                    <i class="fas fa-file-${this.getFileIcon(invoice.type)}"></i>
                </div>
                <div class="invoice-details">
                    <div class="invoice-name">${invoice.name}</div>
                    <div class="invoice-meta">
                        ${invoice.vendor} • $${invoice.amount} • ${date.toLocaleDateString()}
                    </div>
                </div>
                <div class="invoice-actions">
                    <span class="status-badge status-active">${invoice.status}</span>
                    <button class="btn-icon" onclick="alert('View invoice: ${invoice.name}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn-icon" onclick="alert('Download: ${invoice.name}')">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            </div>
        `;
    }

    getFileIcon(type) {
        if (type.includes('pdf')) return 'pdf';
        if (type.includes('image')) return 'image';
        return 'file';
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
}

// ==================== Catering Quote Generator ====================

class CateringQuoteGenerator {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.quote = {
            eventName: '',
            clientName: '',
            eventDate: '',
            guestCount: 50,
            items: [],
            taxRate: 0.08,
            gratuity: 0.18
        };
        this.init();
    }

    init() {
        if (!this.container) return;
        this.render();
    }

    render() {
        const subtotal = this.calculateSubtotal();
        const tax = subtotal * this.quote.taxRate;
        const gratuity = subtotal * this.quote.gratuity;
        const total = subtotal + tax + gratuity;

        const html = `
            <div class="quote-generator">
                <div class="quote-header">
                    <h3>Catering Quote Generator</h3>
                    <button class="btn btn-primary" onclick="window.quoteGen.generatePDF()">
                        <i class="fas fa-file-pdf"></i> Generate PDF
                    </button>
                </div>

                <div class="quote-form">
                    <div class="form-grid">
                        <div class="form-group">
                            <label>Event Name</label>
                            <input type="text" id="eventName" placeholder="Wedding Reception"
                                   value="${this.quote.eventName}">
                        </div>
                        <div class="form-group">
                            <label>Client Name</label>
                            <input type="text" id="clientName" placeholder="John & Jane Doe"
                                   value="${this.quote.clientName}">
                        </div>
                        <div class="form-group">
                            <label>Event Date</label>
                            <input type="date" id="eventDate" value="${this.quote.eventDate}">
                        </div>
                        <div class="form-group">
                            <label>Guest Count</label>
                            <input type="number" id="guestCount" min="1" value="${this.quote.guestCount}">
                        </div>
                    </div>
                </div>

                <div class="quote-items">
                    <div class="items-header">
                        <h4>Menu Items</h4>
                        <button class="btn btn-secondary" onclick="window.quoteGen.addItem()">
                            <i class="fas fa-plus"></i> Add Item
                        </button>
                    </div>
                    <div id="itemsList">
                        ${this.quote.items.length === 0 ?
                            '<p class="no-items">No items added yet</p>' :
                            this.quote.items.map((item, idx) => this.renderItem(item, idx)).join('')
                        }
                    </div>
                </div>

                <div class="quote-summary">
                    <div class="summary-row">
                        <span>Subtotal:</span>
                        <strong>$${subtotal.toFixed(2)}</strong>
                    </div>
                    <div class="summary-row">
                        <span>Tax (${(this.quote.taxRate * 100).toFixed(0)}%):</span>
                        <strong>$${tax.toFixed(2)}</strong>
                    </div>
                    <div class="summary-row">
                        <span>Gratuity (${(this.quote.gratuity * 100).toFixed(0)}%):</span>
                        <strong>$${gratuity.toFixed(2)}</strong>
                    </div>
                    <div class="summary-row total-row">
                        <span>Total:</span>
                        <strong>$${total.toFixed(2)}</strong>
                    </div>
                    <div class="summary-row">
                        <span>Per Person:</span>
                        <strong>$${(total / this.quote.guestCount).toFixed(2)}</strong>
                    </div>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
        this.attachEvents();
    }

    attachEvents() {
        // Input events
        const inputs = ['eventName', 'clientName', 'eventDate', 'guestCount'];
        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', (e) => {
                    this.quote[id] = e.target.value;
                    this.updateSummary();
                });
            }
        });
    }

    addItem() {
        this.quote.items.push({
            name: 'New Item',
            description: '',
            quantity: 1,
            unitPrice: 0
        });
        this.render();
    }

    removeItem(index) {
        this.quote.items.splice(index, 1);
        this.render();
    }

    updateItem(index, field, value) {
        if (this.quote.items[index]) {
            this.quote.items[index][field] = value;
            this.updateSummary();
        }
    }

    renderItem(item, index) {
        return `
            <div class="quote-item">
                <input type="text" class="item-name" placeholder="Item name"
                       value="${item.name}"
                       onchange="window.quoteGen.updateItem(${index}, 'name', this.value)">
                <input type="text" class="item-desc" placeholder="Description"
                       value="${item.description}"
                       onchange="window.quoteGen.updateItem(${index}, 'description', this.value)">
                <input type="number" class="item-qty" placeholder="Qty" min="1"
                       value="${item.quantity}"
                       onchange="window.quoteGen.updateItem(${index}, 'quantity', parseFloat(this.value))">
                <input type="number" class="item-price" placeholder="$0.00" min="0" step="0.01"
                       value="${item.unitPrice}"
                       onchange="window.quoteGen.updateItem(${index}, 'unitPrice', parseFloat(this.value))">
                <div class="item-total">$${(item.quantity * item.unitPrice).toFixed(2)}</div>
                <button class="btn-remove" onclick="window.quoteGen.removeItem(${index})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    }

    calculateSubtotal() {
        return this.quote.items.reduce((sum, item) =>
            sum + (item.quantity * item.unitPrice), 0
        );
    }

    updateSummary() {
        const subtotal = this.calculateSubtotal();
        const tax = subtotal * this.quote.taxRate;
        const gratuity = subtotal * this.quote.gratuity;
        const total = subtotal + tax + gratuity;

        const summary = document.querySelector('.quote-summary');
        if (summary) {
            summary.innerHTML = `
                <div class="summary-row">
                    <span>Subtotal:</span>
                    <strong>$${subtotal.toFixed(2)}</strong>
                </div>
                <div class="summary-row">
                    <span>Tax (${(this.quote.taxRate * 100).toFixed(0)}%):</span>
                    <strong>$${tax.toFixed(2)}</strong>
                </div>
                <div class="summary-row">
                    <span>Gratuity (${(this.quote.gratuity * 100).toFixed(0)}%):</span>
                    <strong>$${gratuity.toFixed(2)}</strong>
                </div>
                <div class="summary-row total-row">
                    <span>Total:</span>
                    <strong>$${total.toFixed(2)}</strong>
                </div>
                <div class="summary-row">
                    <span>Per Person:</span>
                    <strong>$${this.quote.guestCount > 0 ? (total / this.quote.guestCount).toFixed(2) : '0.00'}</strong>
                </div>
            `;
        }
    }

    loadSampleQuote() {
        this.quote = {
            eventName: 'Corporate Holiday Party',
            clientName: 'Tech Corp Inc.',
            eventDate: '2024-12-15',
            guestCount: 100,
            items: [
                { name: 'Appetizer Platter', description: 'Assorted finger foods', quantity: 10, unitPrice: 45.00 },
                { name: 'Chicken Entree', description: 'Grilled chicken breast', quantity: 60, unitPrice: 18.50 },
                { name: 'Vegetarian Entree', description: 'Pasta primavera', quantity: 40, unitPrice: 15.00 },
                { name: 'Dessert Table', description: 'Assorted desserts', quantity: 1, unitPrice: 300.00 }
            ],
            taxRate: 0.08,
            gratuity: 0.18
        };
        this.render();
    }

    generatePDF() {
        // Check if jsPDF is loaded
        if (typeof window.jspdf === 'undefined') {
            notifications.show('PDF library not loaded. Loading now...', 'info');
            this.loadJsPDF(() => this.createPDF());
            return;
        }

        this.createPDF();
    }

    loadJsPDF(callback) {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
        script.onload = callback;
        document.head.appendChild(script);
    }

    createPDF() {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        // Header
        doc.setFontSize(20);
        doc.setFont(undefined, 'bold');
        doc.text('THE LARIAT BIBLE', 105, 20, { align: 'center' });

        doc.setFontSize(16);
        doc.text('Catering Quote', 105, 30, { align: 'center' });

        // Event Details
        doc.setFontSize(12);
        doc.setFont(undefined, 'normal');
        doc.text(`Event: ${this.quote.eventName || 'N/A'}`, 20, 50);
        doc.text(`Client: ${this.quote.clientName || 'N/A'}`, 20, 58);
        doc.text(`Date: ${this.quote.eventDate || 'N/A'}`, 20, 66);
        doc.text(`Guests: ${this.quote.guestCount}`, 20, 74);

        // Items Header
        doc.setFont(undefined, 'bold');
        doc.text('Menu Items', 20, 90);

        // Items
        let y = 100;
        doc.setFont(undefined, 'normal');
        this.quote.items.forEach((item, idx) => {
            const total = item.quantity * item.unitPrice;
            doc.text(`${item.name}`, 20, y);
            doc.text(`${item.description}`, 25, y + 5, { maxWidth: 100 });
            doc.text(`Qty: ${item.quantity} × $${item.unitPrice.toFixed(2)}`, 140, y);
            doc.text(`$${total.toFixed(2)}`, 180, y);
            y += 15;
        });

        // Summary
        const subtotal = this.calculateSubtotal();
        const tax = subtotal * this.quote.taxRate;
        const gratuity = subtotal * this.quote.gratuity;
        const total = subtotal + tax + gratuity;

        y += 10;
        doc.line(20, y, 190, y);
        y += 10;

        doc.text('Subtotal:', 140, y);
        doc.text(`$${subtotal.toFixed(2)}`, 180, y);
        y += 8;

        doc.text(`Tax (${(this.quote.taxRate * 100).toFixed(0)}%):`, 140, y);
        doc.text(`$${tax.toFixed(2)}`, 180, y);
        y += 8;

        doc.text(`Gratuity (${(this.quote.gratuity * 100).toFixed(0)}%):`, 140, y);
        doc.text(`$${gratuity.toFixed(2)}`, 180, y);
        y += 8;

        doc.setFont(undefined, 'bold');
        doc.text('Total:', 140, y);
        doc.text(`$${total.toFixed(2)}`, 180, y);

        // Save
        const filename = `quote-${this.quote.clientName || 'client'}-${Date.now()}.pdf`;
        doc.save(filename);

        notifications.show('PDF generated successfully!', 'success');
    }
}

// ==================== Inventory Alert System ====================

class InventoryAlertSystem {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.items = this.generateSampleInventory();
        this.alertThreshold = 20; // Alert when stock < 20%
        this.init();
    }

    init() {
        if (!this.container) return;
        this.render();
        this.checkAlerts();
    }

    generateSampleInventory() {
        return [
            { id: 1, name: 'Olive Oil', category: 'Cooking Oil', current: 5, max: 30, unit: 'gallons', status: 'critical' },
            { id: 2, name: 'Flour', category: 'Dry Goods', current: 25, max: 100, unit: 'lbs', status: 'low' },
            { id: 3, name: 'Chicken Breast', category: 'Protein', current: 50, max: 100, unit: 'lbs', status: 'good' },
            { id: 4, name: 'Tomatoes', category: 'Produce', current: 10, max: 50, unit: 'lbs', status: 'low' },
            { id: 5, name: 'Mozzarella', category: 'Dairy', current: 15, max: 40, unit: 'lbs', status: 'low' },
            { id: 6, name: 'Pasta', category: 'Dry Goods', current: 80, max: 100, unit: 'lbs', status: 'good' },
            { id: 7, name: 'Ground Beef', category: 'Protein', current: 3, max: 50, unit: 'lbs', status: 'critical' },
            { id: 8, name: 'Lettuce', category: 'Produce', current: 35, max: 40, unit: 'heads', status: 'good' }
        ];
    }

    render() {
        const lowStockItems = this.items.filter(item => this.getStockPercentage(item) < this.alertThreshold);
        const criticalItems = this.items.filter(item => item.status === 'critical');

        const html = `
            <div class="inventory-alerts">
                <div class="alerts-header">
                    <h3>Inventory Alerts</h3>
                    <div class="alert-summary">
                        <span class="alert-badge critical">${criticalItems.length} Critical</span>
                        <span class="alert-badge warning">${lowStockItems.length} Low Stock</span>
                    </div>
                </div>

                <div class="inventory-grid">
                    ${this.items.map(item => this.renderInventoryItem(item)).join('')}
                </div>

                <div class="quick-order">
                    <button class="btn btn-primary" onclick="window.inventoryAlerts.quickOrder()">
                        <i class="fas fa-shopping-cart"></i> Quick Order Low Stock Items
                    </button>
                </div>
            </div>
        `;

        this.container.innerHTML = html;
    }

    renderInventoryItem(item) {
        const percentage = this.getStockPercentage(item);
        const statusClass = item.status;
        const progressColor = this.getProgressColor(percentage);

        return `
            <div class="inventory-item ${statusClass}">
                <div class="item-header">
                    <div class="item-info">
                        <h4>${item.name}</h4>
                        <span class="item-category">${item.category}</span>
                    </div>
                    <span class="status-badge status-${statusClass}">${item.status}</span>
                </div>
                <div class="item-stock">
                    <div class="stock-numbers">
                        <span class="current">${item.current} ${item.unit}</span>
                        <span class="max">/ ${item.max} ${item.unit}</span>
                    </div>
                    <div class="stock-bar">
                        <div class="stock-fill ${progressColor}" style="width: ${percentage}%"></div>
                    </div>
                    <div class="stock-percentage">${percentage.toFixed(0)}%</div>
                </div>
                <div class="item-actions">
                    <button class="btn-sm" onclick="window.inventoryAlerts.updateStock(${item.id}, 10)">
                        <i class="fas fa-plus"></i> Add 10
                    </button>
                    <button class="btn-sm" onclick="window.inventoryAlerts.orderItem(${item.id})">
                        <i class="fas fa-shopping-cart"></i> Order
                    </button>
                </div>
            </div>
        `;
    }

    getStockPercentage(item) {
        return (item.current / item.max) * 100;
    }

    getProgressColor(percentage) {
        if (percentage < 10) return 'critical';
        if (percentage < 20) return 'warning';
        return 'good';
    }

    updateStock(itemId, amount) {
        const item = this.items.find(i => i.id === itemId);
        if (item) {
            item.current = Math.min(item.current + amount, item.max);
            item.status = this.calculateStatus(item);
            this.render();
            notifications.show(`Updated ${item.name} stock`, 'success');
        }
    }

    calculateStatus(item) {
        const percentage = this.getStockPercentage(item);
        if (percentage < 10) return 'critical';
        if (percentage < 20) return 'low';
        return 'good';
    }

    orderItem(itemId) {
        const item = this.items.find(i => i.id === itemId);
        if (item) {
            const orderAmount = item.max - item.current;
            notifications.show(
                `Ordering ${orderAmount} ${item.unit} of ${item.name}`,
                'info'
            );
        }
    }

    quickOrder() {
        const lowStockItems = this.items.filter(item => this.getStockPercentage(item) < this.alertThreshold);

        if (lowStockItems.length === 0) {
            notifications.show('No items need ordering', 'info');
            return;
        }

        notifications.show(
            `Ordering ${lowStockItems.length} low stock items`,
            'success'
        );

        // Simulate ordering
        lowStockItems.forEach(item => {
            setTimeout(() => {
                item.current = item.max;
                item.status = 'good';
                this.render();
            }, 1000);
        });
    }

    checkAlerts() {
        const criticalItems = this.items.filter(item => item.status === 'critical');

        if (criticalItems.length > 0) {
            criticalItems.forEach(item => {
                notifications.show(
                    `CRITICAL: ${item.name} is at ${item.current} ${item.unit}!`,
                    'error',
                    10000 // Show for 10 seconds
                );
            });
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('invoiceUploader')) {
        window.invoiceUploader = new InvoiceUploader('invoiceUploader');
    }

    if (document.getElementById('quoteGenerator')) {
        window.quoteGen = new CateringQuoteGenerator('quoteGenerator');
    }

    if (document.getElementById('inventoryAlerts')) {
        window.inventoryAlerts = new InventoryAlertSystem('inventoryAlerts');
    }
});

console.log('✨ Advanced interactive features loaded');
