# Templates Directory

## Master Templates - Do Not Edit Directly

This directory contains the master templates for the BEO Bible system. These files should **never be edited directly**. Instead, copy them to the appropriate event folder in `ACTIVE_EVENTS/` before making any changes.

## Files

### Invoice_Template_MASTER.xlsx
**Purpose**: Master invoice template with automated pricing and kitchen prep sheets

**Contains**:
- **Sheet 1: Client Invoice**
  - Item names and quantities
  - VLOOKUP pricing formulas
  - Automatic calculations (subtotal, tax, service fee)
  - Minimum spend validation
  - 53-item price lookup table (columns F:G)

- **Sheet 2: Kitchen Prep Sheet**
  - Auto-populated from Sheet 1 (linked formulas)
  - Prep day assignments (Thursday/Friday/Saturday)
  - Task details and instructions
  - Plating specifications
  - Service timing notes

**How to Use**:
1. Copy this file to `ACTIVE_EVENTS/ClientName_EventDate/`
2. Rename to `Invoice_ClientName_Date_v1.xlsx`
3. Fill in client information and menu selections
4. Sheet 2 will automatically populate
5. Save new versions (v2, v3, etc.) for revisions

**Do Not**:
- Edit this master file directly
- Delete or modify the formulas
- Change the price lookup table structure
- Remove Sheet 2 linkages

## Template Maintenance

### Updating Prices
1. Create a backup of the master template
2. Update the price lookup table in columns F:G on Sheet 1
3. Verify all VLOOKUP formulas still work correctly
4. Test with a sample event
5. Document changes in NOTES.txt with date

### Adding Menu Items
1. Add new item to the price lookup table (F:G columns)
2. Ensure item names match exactly (case-sensitive)
3. Test VLOOKUP formula with new item
4. Update recipe book reference if needed

### Version Control
- Master template version: 1.0
- Last updated: 2025-11-19
- Next review: Monthly

## Support

For questions about template usage, see:
- [DOCUMENTATION/PROJECT_RULES.md](../DOCUMENTATION/PROJECT_RULES.md) - Formula specifications
- [DOCUMENTATION/WORKFLOW.md](../DOCUMENTATION/WORKFLOW.md) - Step-by-step usage
- [DOCUMENTATION/SYSTEM_OVERVIEW.md](../DOCUMENTATION/SYSTEM_OVERVIEW.md) - Feature overview
