# Invoice Photo Processing Guide

## 📸 Overview

The Lariat Bible now includes a powerful **Invoice OCR System** that automatically extracts data from invoice photos. This system can:

- ✅ Extract **distributor names** (SYSCO, Shamrock Foods, US Foods, etc.)
- ✅ Extract **invoice numbers and order numbers**
- ✅ Extract **dates** (invoice date, delivery date)
- ✅ Extract **line items** with:
  - Item codes
  - Product descriptions
  - Pack sizes
  - Quantities
  - Unit prices
  - Total prices
- ✅ Extract **totals** (subtotal, tax, grand total)
- ✅ Export data to **JSON and CSV** formats

## 🚀 Quick Start

### Prerequisites

Make sure you have Tesseract OCR installed:

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH or specify path when running

### Installation

All required Python packages are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `pytesseract` - OCR engine
- `opencv-python` - Image preprocessing
- `Pillow` - Image handling
- `rich` - Beautiful terminal output

## 📝 Usage

### Process a Single Invoice

```bash
python process_invoices.py -i path/to/invoice.jpg
```

Example:
```bash
python process_invoices.py -i data/invoices/sysco_invoice_12345.jpg
```

### Process All Invoices in a Directory

```bash
python process_invoices.py -d data/invoices/
```

### Process and Save Results

```bash
python process_invoices.py -d data/invoices/ -o data/processed/
```

This will create:
- `{invoice_name}_data.json` - Complete invoice data in JSON format
- `{invoice_name}_items.csv` - Line items in CSV format for easy import

### Custom Tesseract Path (Windows)

If Tesseract is not in your PATH:

```bash
python process_invoices.py -i invoice.jpg --tesseract "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## 📊 Sample Output

```
═══════════════════════════════════════════
   THE LARIAT - Invoice Photo Processor
═══════════════════════════════════════════

Processing: data/invoices/sysco_invoice.jpg

Step 1: Extracting text from image...
  ✓ Extracted 1247 characters
  ✓ Confidence: 87.3%

Step 2: Extracting structured data...

═══ EXTRACTED INVOICE DATA ═══

Distributor:      SYSCO
Invoice Number:   INV-2024-12345
Order Number:     PO-98765
Invoice Date:     2024-11-18
Delivery Date:    2024-11-19

Line Items: (15 items found)

┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Code     ┃ Description         ┃ Pack  ┃  Qty ┃ Unit Price┃    Total ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│ 123456   │ PEPPER BLACK GROUND │ 6/1#  │  2.0 │    $45.99 │  $91.98  │
│ 234567   │ SALT KOSHER         │ 25 LB │  1.0 │    $12.50 │  $12.50  │
│ 345678   │ TOMATO PASTE        │ 6/#10 │  3.0 │    $28.75 │  $86.25  │
└──────────┴─────────────────────┴───────┴──────┴───────────┴──────────┘

Totals:
Subtotal:     $2,450.00
Tax:          $196.00
Total:        $2,646.00

✓ Saved JSON: data/processed/sysco_invoice_data.json
✓ Saved CSV: data/processed/sysco_invoice_items.csv
```

## 🔧 Advanced Usage

### Using in Python Code

```python
from modules.invoice_ocr import InvoiceProcessor, InvoiceDataExtractor

# Initialize
processor = InvoiceProcessor()
extractor = InvoiceDataExtractor()

# Process invoice photo
ocr_result = processor.process_invoice('invoice.jpg')

# Extract structured data
invoice_data = extractor.extract_all(ocr_result['raw_text'])

# Access data
print(f"Distributor: {invoice_data.distributor}")
print(f"Invoice #: {invoice_data.invoice_number}")
print(f"Total: ${invoice_data.total}")

# Iterate over items
for item in invoice_data.items:
    print(f"{item.description}: ${item.total_price}")

# Export to JSON
extractor.export_to_json(invoice_data, 'output.json')

# Export to CSV
extractor.export_to_csv(invoice_data, 'output.csv')
```

### Batch Processing with Custom Logic

```python
from modules.invoice_ocr import InvoiceProcessor, InvoiceDataExtractor
from pathlib import Path

processor = InvoiceProcessor()
extractor = InvoiceDataExtractor()

# Process all invoices
invoice_dir = Path('data/invoices')
all_invoices = []

for image_path in invoice_dir.glob('*.jpg'):
    # Process
    ocr_result = processor.process_invoice(str(image_path))
    invoice_data = extractor.extract_all(ocr_result['raw_text'])

    # Store
    all_invoices.append(invoice_data)

# Analyze across all invoices
total_amount = sum(inv.total for inv in all_invoices if inv.total)
print(f"Total across all invoices: ${total_amount:,.2f}")

# Group by distributor
from collections import defaultdict
by_distributor = defaultdict(list)

for inv in all_invoices:
    by_distributor[inv.distributor].append(inv)

for distributor, invoices in by_distributor.items():
    print(f"{distributor}: {len(invoices)} invoices")
```

## 📁 Output Formats

### JSON Format

```json
{
  "distributor": "SYSCO",
  "invoice_number": "INV-2024-12345",
  "order_number": "PO-98765",
  "invoice_date": "2024-11-18T00:00:00",
  "delivery_date": "2024-11-19T00:00:00",
  "items": [
    {
      "item_code": "123456",
      "description": "PEPPER BLACK GROUND",
      "quantity": 2.0,
      "unit_price": 45.99,
      "total_price": 91.98,
      "pack_size": "6/1#"
    }
  ],
  "subtotal": 2450.00,
  "tax": 196.00,
  "total": 2646.00
}
```

### CSV Format

```csv
distributor,invoice_number,order_number,invoice_date,item_code,description,pack_size,quantity,unit_price,total_price
SYSCO,INV-2024-12345,PO-98765,2024-11-18,123456,PEPPER BLACK GROUND,6/1#,2.0,45.99,91.98
SYSCO,INV-2024-12345,PO-98765,2024-11-18,234567,SALT KOSHER,25 LB,1.0,12.50,12.50
```

## 🎯 Tips for Best Results

### Photo Quality

1. **Good Lighting** - Ensure invoice is well-lit with minimal shadows
2. **Flat Surface** - Place invoice on flat surface to avoid distortion
3. **High Resolution** - Use at least 300 DPI for best OCR results
4. **Straight Alignment** - Try to keep invoice straight (system will auto-deskew minor angles)
5. **Clear Text** - Avoid blurry photos; use camera focus

### Supported Distributors

The system recognizes these distributors automatically:
- SYSCO (various entities)
- Shamrock Foods
- US Foods
- Performance Food Group (PFG)
- Gordon Food Service (GFS)

Others will be marked as "UNKNOWN" but data extraction will still work.

### File Organization

Recommended directory structure:

```
data/
├── invoices/
│   ├── raw/              # Original invoice photos
│   │   ├── 2024-11-18_sysco_001.jpg
│   │   └── 2024-11-18_shamrock_002.jpg
│   └── processed/        # Extracted data
│       ├── 2024-11-18_sysco_001_data.json
│       ├── 2024-11-18_sysco_001_items.csv
│       ├── 2024-11-18_shamrock_002_data.json
│       └── 2024-11-18_shamrock_002_items.csv
```

## 🔍 How It Works

### 1. Image Preprocessing

The system automatically:
- Converts to grayscale
- Applies denoising filters
- Adjusts contrast with adaptive thresholding
- Detects and corrects skew (rotation)
- Enhances text for OCR

### 2. OCR Text Extraction

Uses Google's Tesseract OCR engine to:
- Extract all text from the invoice
- Identify text positions and confidence scores
- Maintain line and block structure

### 3. Data Extraction

Intelligent pattern matching to extract:
- **Distributor**: Matches against known vendor names
- **Dates**: Multiple date format support (MM/DD/YYYY, etc.)
- **Invoice/Order Numbers**: Flexible pattern recognition
- **Line Items**: Parses item codes, descriptions, quantities, prices
- **Totals**: Extracts subtotal, tax, and total amounts

### 4. Data Export

Saves extracted data in:
- **JSON**: Complete structured data for APIs and databases
- **CSV**: Easy import into Excel, Google Sheets, or databases

## 🐛 Troubleshooting

### "Tesseract not found" Error

**Problem:** Tesseract OCR is not installed or not in PATH

**Solutions:**
1. Install Tesseract (see Prerequisites section)
2. Add Tesseract to system PATH
3. Use `--tesseract` flag to specify path manually

### Low OCR Confidence

**Problem:** Confidence score below 70%

**Solutions:**
1. Retake photo with better lighting
2. Increase image resolution
3. Ensure invoice is flat and not wrinkled
4. Clean camera lens

### Missing Line Items

**Problem:** Some items not extracted

**Solutions:**
1. Check if invoice format is standard
2. Manually review raw OCR text output
3. May need to customize extraction patterns for specific vendor formats

### Wrong Distributor Detected

**Problem:** Distributor shown as "UNKNOWN"

**Solution:**
- Add distributor pattern to `DISTRIBUTORS` dict in `data_extractor.py`
- Submit issue/PR with distributor name and invoice format

## 🔮 Future Enhancements

Planned features:
- [ ] Machine learning-based line item extraction
- [ ] Support for PDF invoices
- [ ] Automatic vendor price comparison after extraction
- [ ] Email integration (auto-process attachments)
- [ ] Mobile app for on-the-go scanning
- [ ] Database integration for automatic storage
- [ ] Duplicate invoice detection

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review error messages carefully
3. Ensure Tesseract is properly installed
4. Contact Sean for vendor-specific invoice format issues

---

**Built for The Lariat Restaurant** 🤠
*Making invoice processing fast, accurate, and automated*
