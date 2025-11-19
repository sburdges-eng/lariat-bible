# Vendor Import Template Guide

## Overview

The Lariat Bible provides standardized import templates for SYSCO and Shamrock Foods vendor catalogs. This guide explains how to use these templates to import product data, pricing information, and vendor catalogs into the system.

## 📋 Available Templates

### 1. SYSCO Import Template (`SYSCO_IMPORT_TEMPLATE.csv`)
- **Vendor**: SYSCO Corporation
- **Format**: CSV (UTF-8)
- **Product Code Format**: 7-digit numeric code (e.g., `8123456`)
- **SKU Format**: `SYS-{product_code}` (e.g., `SYS-8123456`)

### 2. Shamrock Foods Import Template (`SHAMROCK_IMPORT_TEMPLATE.csv`)
- **Vendor**: Shamrock Foods Company
- **Format**: CSV (UTF-8)
- **Product Code Format**: `SF-{6-digit number}` (e.g., `SF-892345`)
- **SKU Format**: `SHAM-{6-digit number}` (e.g., `SHAM-892345`)

## 📥 Download Templates

### Via Web Interface
1. Navigate to the Vendors tab
2. Click "Import Products"
3. Select vendor (SYSCO or Shamrock)
4. Click "Download Template"

### Via API
```bash
# Download SYSCO template
curl -O http://localhost:5000/api/vendor/import/template/SYSCO

# Download Shamrock template
curl -O http://localhost:5000/api/vendor/import/template/SHAMROCK
```

### Direct File Access
Templates are located in:
```
/home/user/lariat-bible/data/templates/
├── SYSCO_IMPORT_TEMPLATE.csv
├── SYSCO_SCHEMA.json
├── SHAMROCK_IMPORT_TEMPLATE.csv
└── SHAMROCK_SCHEMA.json
```

## 📊 Template Structure

### Required Fields

Both templates include these **required** fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `{vendor}_product_code` | String | Vendor's product code | `8123456` or `SF-892345` |
| `product_name` | String | Full product name | `Black Pepper Fine Grind` |
| `category` | String | Primary category | `Spices & Seasonings` |
| `pack_size` | String | Package size description | `5 LB` or `6/5 LB` |
| `unit_of_measure` | String | Unit (LB, OZ, EACH, etc.) | `LB` |
| `case_price` | Number | Price per case (USD) | `246.57` |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `brand` | String | Brand name |
| `subcategory` | String | Product subcategory |
| `unit_price` | Number | Price per unit |
| `price_per_lb` | Number | Price per pound |
| `price_per_oz` | Number | Price per ounce |
| `each_weight_lb` | Number | Weight of each unit (lb) |
| `case_quantity` | Integer | Units per case |
| `vendor_sku` | String | Internal SKU |
| `upc_code` | String | 12-digit UPC |
| `description` | String | Detailed description |
| `allergen_info` | String | Allergen information |
| `storage_temp` | String | Ambient/Refrigerated/Frozen |
| `shelf_life_days` | Integer | Shelf life in days |
| `country_of_origin` | String | Country of origin |
| `kosher` | String | Y/N |
| `organic` | String | Y/N |
| `gluten_free` | String | Y/N |
| `non_gmo` | String | Y/N |
| `last_updated` | Date | Last update (YYYY-MM-DD) |

## 📝 Field Specifications

### Product Codes

**SYSCO**:
- Format: 7-digit number
- Pattern: `^[0-9]{7}$`
- Example: `8123456`

**Shamrock**:
- Format: `SF-` followed by 6 digits
- Pattern: `^SF-[0-9]{6}$`
- Example: `SF-892345`

### Categories

Valid categories (both vendors):
- Spices & Seasonings
- Meat & Poultry
- Produce
- Dairy
- Frozen Foods
- Condiments
- Bakery
- Beverages
- Dry Goods
- Seafood
- Deli

### Units of Measure

Valid units:
- `LB` - Pounds
- `OZ` - Ounces
- `KG` - Kilograms
- `EACH` - Each/Individual
- `GAL` - Gallons
- `QT` - Quarts
- `PT` - Pints
- `L` - Liters
- `ML` - Milliliters
- `CT` - Count

### Storage Temperature

Valid values:
- `Ambient` - Room temperature
- `Refrigerated` - 32-40°F
- `Frozen` - Below 0°F

## 🔍 Data Validation Rules

The import system validates data according to these rules:

### 1. Required Field Validation
- All required fields must have values
- Empty or whitespace-only values are rejected

### 2. Numeric Validation
- All prices must be positive numbers
- Quantities must be positive integers
- Decimal values use period (`.`) as separator

### 3. Price Consistency
The system checks:
```
case_price ≈ unit_price × case_quantity
```
Tolerance: ±$0.02

### 4. Weight Consistency
If both provided:
```
price_per_oz ≈ price_per_lb / 16
```

### 5. Format Validation
- Product codes must match vendor-specific patterns
- UPC codes must be exactly 12 digits
- Dates must be in `YYYY-MM-DD` format

### 6. Enum Validation
- Categories must be from predefined list
- Units of measure must be valid
- Boolean fields (kosher, organic, etc.) must be `Y` or `N`

## 📤 Importing Data

### Method 1: Web Interface

1. **Navigate to Vendors Tab**
   - Open the web UI: `http://localhost:5000`
   - Click on the "Vendors" tab
   - Click "Import Products" button

2. **Select Vendor**
   - Choose SYSCO or Shamrock Foods
   - Download template if needed

3. **Prepare Your File**
   - Fill in product data using template
   - Save as CSV (UTF-8 encoding)
   - Ensure all required fields are populated

4. **Upload File**
   - Click "Choose File"
   - Select your CSV file
   - Click "Upload & Validate"

5. **Review Validation Results**
   - System validates file automatically
   - View any errors or warnings
   - Fix issues if needed

6. **Import Products**
   - If validation passes, click "Import Products"
   - View import progress
   - Review import summary

### Method 2: API

#### Upload and Validate
```bash
curl -X POST http://localhost:5000/api/vendor/import/upload \
  -F "file=@sysco_products.csv" \
  -F "vendor=SYSCO"
```

Response:
```json
{
  "success": true,
  "filename": "SYSCO_20251119_143022_sysco_products.csv",
  "filepath": "data/uploads/SYSCO_20251119_143022_sysco_products.csv",
  "validation": {
    "valid": true,
    "row_count": 20,
    "errors": [],
    "warnings": []
  }
}
```

#### Process Import
```bash
curl -X POST http://localhost:5000/api/vendor/import/process \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "data/uploads/SYSCO_20251119_143022_sysco_products.csv",
    "vendor": "SYSCO"
  }'
```

Response:
```json
{
  "success": true,
  "result": {
    "vendor": "SYSCO",
    "total_rows": 20,
    "successful_imports": 20,
    "failed_imports": 0,
    "success_rate": 100.0,
    "products": [...],
    "errors": []
  }
}
```

### Method 3: Python Script

```python
from modules.vendor_import import VendorImporter

# Initialize importer
importer = VendorImporter()

# Validate file first
validation = importer.validate_import_file('sysco_products.csv', 'SYSCO')

if validation['valid']:
    # Import products
    result = importer.import_sysco_products('sysco_products.csv')

    print(f"Imported {result['successful_imports']} products")
    print(f"Failed: {result['failed_imports']}")

    # Display any errors
    for error in result['errors']:
        print(f"Error: {error}")
else:
    print("Validation failed:")
    for error in validation['errors']:
        print(f"  - {error}")
```

## 🚨 Common Errors and Solutions

### Error: "Missing required field: product_name"
**Solution**: Ensure all required fields have values. Check for empty cells.

### Error: "Invalid SYSCO product code format"
**Solution**: SYSCO codes must be exactly 7 digits (no letters, no hyphens).

### Error: "Invalid Shamrock product code format"
**Solution**: Shamrock codes must start with `SF-` followed by 6 digits.

### Error: "Invalid value for case_price"
**Solution**: Prices must be positive numbers. Use period (.) as decimal separator, not comma.

### Error: "Price mismatch"
**Warning**: Case price doesn't match unit_price × case_quantity. This is a warning, not an error. Verify your pricing data.

### Error: "Invalid category"
**Solution**: Category must be one of the predefined values. Check spelling and capitalization.

### Error: "Invalid file type"
**Solution**: Only CSV files are supported. Ensure file extension is `.csv`.

## 💡 Best Practices

### 1. Use Templates
- Always start with the official template
- Don't add or remove columns
- Don't change column order

### 2. Data Quality
- Fill in as many optional fields as possible
- Provide accurate pricing information
- Include allergen information for food safety
- Add descriptive product descriptions

### 3. Validation Before Import
- Always validate files before importing
- Fix all errors before processing
- Review warnings carefully

### 4. Incremental Updates
- Import products in batches
- Test with small samples first
- Keep backup of original data

### 5. Regular Updates
- Update product data regularly
- Re-import when prices change
- Archive old import files

## 📈 After Import

### View Imported Products
```bash
# Get all vendors
curl http://localhost:5000/api/vendors

# View import history
curl http://localhost:5000/api/vendor/import/history
```

### Compare Prices
After importing both SYSCO and Shamrock products:

```python
from modules.vendor_import import VendorImporter

importer = VendorImporter()

# Import both vendors
sysco_result = importer.import_sysco_products('sysco.csv')
shamrock_result = importer.import_shamrock_products('shamrock.csv')

# Compare pricing
comparisons = importer.compare_vendor_pricing(
    sysco_result['products'],
    shamrock_result['products']
)

# Export comparison
importer.export_comparison_to_csv(comparisons, 'price_comparison.csv')
```

## 🔒 Security Notes

### Production Deployment

1. **File Upload Security**
   - Validate file types strictly
   - Scan uploaded files for malware
   - Limit file sizes (current: 16MB)
   - Use secure file storage

2. **Data Privacy**
   - Don't commit uploaded files to git
   - Upload directory is in `.gitignore`
   - Sanitize file names
   - Implement access controls

3. **API Security**
   - Add authentication for import endpoints
   - Implement rate limiting
   - Log all import activities
   - Validate user permissions

## 📞 Support

### Template Issues
- Check template format matches examples
- Verify CSV encoding is UTF-8
- Ensure no special characters in required fields

### Import Errors
- Review error messages carefully
- Check validation results
- Verify data types match requirements

### API Issues
- Check endpoint URLs
- Verify request format
- Review API response codes

## 📚 Additional Resources

- **JSON Schemas**: `data/templates/SYSCO_SCHEMA.json`, `SHAMROCK_SCHEMA.json`
- **Example Data**: See template CSV files for sample products
- **API Documentation**: See Flask app routes in `app.py`
- **Source Code**: `modules/vendor_import/vendor_importer.py`

---

**Last Updated**: 2025-11-19
**Version**: 1.0.0
**The Lariat Bible - Restaurant Management System**
