# Invoice Storage Directory

## 📁 Purpose

This directory is for storing invoice photos and processed data.

## 🗂️ Recommended Structure

```
invoices/
├── raw/              # Original invoice photos
│   ├── YYYY-MM-DD_vendor_###.jpg
│   └── ...
└── processed/        # Extracted data (JSON/CSV)
    ├── YYYY-MM-DD_vendor_###_data.json
    ├── YYYY-MM-DD_vendor_###_items.csv
    └── ...
```

## 📸 How to Add Invoices

1. **Take Photo**: Use your phone or scanner to capture invoice
2. **Name File**: Use format `YYYY-MM-DD_vendor_number.jpg`
   - Example: `2024-11-18_sysco_12345.jpg`
3. **Place in `raw/`**: Save original photo in the `raw/` subdirectory
4. **Process**: Run the invoice processor:
   ```bash
   python process_invoices.py -d data/invoices/raw/ -o data/invoices/processed/
   ```

## 📊 Output Files

After processing, you'll get:
- `*_data.json` - Complete invoice data
- `*_items.csv` - Line items in spreadsheet format

## 🎯 Tips

- Keep original photos in `raw/` - never delete
- Review extracted data for accuracy
- File naming convention helps with organization
- Use good lighting for better OCR results

## 🔗 Learn More

See [INVOICE_OCR_GUIDE.md](../../INVOICE_OCR_GUIDE.md) for complete documentation.
