# Test Fixtures

This directory contains sample data files used for testing.

## Files

- `sample_sysco_guide.json` - Sample SYSCO order guide data
- `sample_shamrock_guide.json` - Sample Shamrock Foods order guide data

## Usage

These fixtures are used by tests to provide consistent, realistic test data without requiring actual vendor order guides or database connections.

## Data Format

Order guide files contain arrays of items with the following structure:

```json
{
  "item_code": "Vendor item code",
  "description": "Product description",
  "pack_size": "Pack size (e.g., '10 LB', '6/1LB')",
  "case_price": 45.99,
  "unit_price": 4.599,
  "unit": "Unit of measure (LB, OZ, EA, etc.)",
  "category": "Product category (MEAT, SPICES, etc.)"
}
```
