# COMPLETE CLAUDE CODE GUIDELINES
## For Lariat Banquet System Development

---

## 📋 TABLE OF CONTENTS

1. [Excel Formula Standards](#excel-formula-standards)
2. [VBA/Macro Development](#vba-macro-development)
3. [Documentation Standards](#documentation-standards)
4. [Using Claude for Coding](#using-claude-for-coding)
5. [Version Control Best Practices](#version-control)
6. [Testing & Quality Assurance](#testing-qa)
7. [Automation & Scripting](#automation-scripting)
8. [Naming Conventions](#naming-conventions)
9. [File Organization](#file-organization)
10. [Troubleshooting & Debugging](#troubleshooting)

---

## 1️⃣ EXCEL FORMULA STANDARDS {#excel-formula-standards}

### Formula Construction Rules

**ALWAYS:**
- Use absolute references (`$F$2:$G$100`) for lookup tables
- Use relative references (`A3`) for data that changes per row
- Use mixed references (`$F2`) when only column OR row should be fixed
- Wrap lookups in error handlers: `IFNA()` or `IFERROR()`
- Add comments in adjacent cells for complex formulas

**NEVER:**
- Hard-code values directly in formulas (use cell references)
- Create circular references
- Use volatile functions unnecessarily (`NOW`, `TODAY`, `RAND`) - they recalculate constantly
- Nest more than 3-4 functions deep (readability suffers)

---

### Standard Formula Patterns

#### Price Lookup (VLOOKUP with error handling):
```excel
=IFNA(VLOOKUP(A3,$F$2:$G$100,2,FALSE),"")
```

**Breakdown:**
- `A3` = Item name (changes per row)
- `$F$2:$G$100` = Price table (fixed location)
- `2` = Return value from column 2 of table
- `FALSE` = Exact match only
- `IFNA(...,"")` = Show blank if item not found (instead of #N/A error)

**Alternative (XLOOKUP - Excel 365+):**
```excel
=IFNA(XLOOKUP(A3,$F$2:$F$100,$G$2:$G$100),"")
```

---

#### Calculation Formulas:

**Line Total:**
```excel
=B3*C3
```
(Unit Price × Quantity)

**Subtotal:**
```excel
=SUM(D3:D25)
```
(Sum all line totals)

**Tax Calculation:**
```excel
=D27*0.0815
```
(Subtotal × 8.15%)

**Better: Reference tax rate from a cell:**
```excel
=D27*$H$2
```
(Where H2 contains 0.0815, labeled "Tax Rate")

**Service Fee:**
```excel
=D27*0.20
```

**Better: Reference fee % from a cell:**
```excel
=D27*$H$3
```
(Where H3 contains 0.20, labeled "Service Fee %")

**Grand Total:**
```excel
=SUM(D27:D29)
```
OR
```excel
=D27+D28+D29
```
(Subtotal + Tax + Service Fee)

**Minimum Spend Check:**
```excel
=E33-D27
```
(Minimum Amount - Subtotal)
- Positive = Over minimum ✅
- Negative = Under minimum ⚠️

---

#### Conditional Formatting Formulas:

**Highlight if under minimum spend:**
```excel
=E34<0
```
Apply to cell E34, format with red fill

**Highlight if item not found in price list:**
```excel
=ISNA(VLOOKUP(A3,$F$2:$G$100,2,FALSE))
```
Apply to row 3, format with yellow fill

---

### Formula Documentation Standard

**For complex formulas, add a comment:**

Right-click cell → Insert Comment → Write:
```
Formula calculates total with 20% service fee
Updates automatically when subtotal changes
Last modified: 2025-11-19 by [Your Name]
```

OR add documentation in adjacent column:

| Column D | Column E (Notes) |
|----------|------------------|
| =B3*C3   | Price × Quantity |
| =D27*0.0815 | Tax: 8.15% of subtotal |

---

### Formula Error Prevention

**Common Errors & Fixes:**

| Error | Cause | Fix |
|-------|-------|-----|
| #N/A | Lookup value not found | Wrap in IFNA() |
| #REF! | Referenced cell deleted | Check and fix references |
| #DIV/0! | Dividing by zero | Add IF(B3=0,"",A3/B3) |
| #VALUE! | Wrong data type | Check that numbers are numbers, not text |
| #NAME? | Excel doesn't recognize formula | Check spelling |

---

## 2️⃣ VBA/MACRO DEVELOPMENT {#vba-macro-development}

### When to Use VBA

**Good Use Cases:**
- Automating repetitive tasks (copying data between sheets)
- Custom buttons for common actions
- Data validation beyond Excel's built-in
- Complex calculations that formulas can't handle
- Generating reports automatically

**Avoid VBA For:**
- Simple formulas (use native Excel)
- Things that require maintenance (formulas are easier to update)
- Tasks users need to understand (VBA is a "black box")

---

### VBA Coding Standards

#### Naming Conventions:
```vb
' Variables - camelCase
Dim itemName As String
Dim totalPrice As Double
Dim rowCounter As Integer

' Constants - UPPER_SNAKE_CASE
Const TAX_RATE As Double = 0.0815
Const SERVICE_FEE As Double = 0.20

' Procedures - PascalCase with verb prefix
Sub UpdateKitchenSheet()
Sub CalculateTotals()
Function GetItemPrice(itemName As String) As Double
```

---

#### Code Structure:
```vb
'==================================================
' Module: InvoiceAutomation
' Purpose: Automates invoice creation and updates
' Created: 2025-11-19
' Author: [Your Name]
'==================================================

Option Explicit  ' Force variable declaration

'--------------------------------------------------
' CONSTANTS
'--------------------------------------------------
Const TAX_RATE As Double = 0.0815
Const SERVICE_FEE_PCT As Double = 0.20

'--------------------------------------------------
' MAIN PROCEDURES
'--------------------------------------------------

Sub UpdateKitchenSheet()
    '---------------------------------------------
    ' Copies invoice items to kitchen sheet
    ' Called by: Button on Invoice sheet
    ' Dependencies: None
    '---------------------------------------------

    On Error GoTo ErrorHandler

    Dim wsInvoice As Worksheet
    Dim wsKitchen As Worksheet
    Dim lastRow As Long
    Dim i As Long

    ' Initialize worksheets
    Set wsInvoice = ThisWorkbook.Sheets("Invoice")
    Set wsKitchen = ThisWorkbook.Sheets("Kitchen Sheet")

    ' Find last row with data
    lastRow = wsInvoice.Cells(Rows.Count, "A").End(xlUp).Row

    ' Clear existing kitchen sheet data
    wsKitchen.Range("A3:B100").ClearContents

    ' Copy data
    For i = 3 To lastRow
        If wsInvoice.Cells(i, 1).Value <> "" Then
            wsKitchen.Cells(i, 1).Value = wsInvoice.Cells(i, 1).Value  ' Item name
            wsKitchen.Cells(i, 2).Value = wsInvoice.Cells(i, 3).Value  ' Quantity
        End If
    Next i

    MsgBox "Kitchen sheet updated successfully!", vbInformation
    Exit Sub

ErrorHandler:
    MsgBox "Error updating kitchen sheet: " & Err.Description, vbCritical
End Sub
```

---

### Best Practices:

#### 1. Always Use Option Explicit
```vb
Option Explicit  ' Put at top of every module
```
Forces you to declare variables, prevents typos

#### 2. Error Handling:
```vb
On Error GoTo ErrorHandler

' Your code here

Exit Sub

ErrorHandler:
    MsgBox "Error: " & Err.Description, vbCritical
    ' Log error if needed
End Sub
```

#### 3. Use Meaningful Variable Names:
```vb
' BAD:
Dim x As Integer
Dim temp As String

' GOOD:
Dim rowCounter As Integer
Dim clientName As String
```

#### 4. Comment Extensively:
```vb
' Calculate total including tax and service fee
totalWithFees = subtotal * (1 + TAX_RATE + SERVICE_FEE_PCT)
```

#### 5. Avoid Select/Activate:
```vb
' BAD (slow and unreliable):
Sheets("Invoice").Select
Range("A1").Select
ActiveCell.Value = "Hello"

' GOOD (direct reference):
Sheets("Invoice").Range("A1").Value = "Hello"
```

---

## 3️⃣ DOCUMENTATION STANDARDS {#documentation-standards}

### Inline Documentation

**Excel Formulas:**
- Add notes in adjacent cells for anything non-obvious
- Use cell comments for complex formulas
- Color-code cells (light yellow = formula, white = input)

**VBA Code:**
- Header comment for every module
- Comment every procedure (what it does, when it's called)
- Comment complex logic inline
- Update comments when code changes

---

### File Documentation

**Every template file should have a "README" sheet:**
```
╔══════════════════════════════════════════════════════════════╗
║                    INVOICE TEMPLATE v2.1                    ║
║                  Last Updated: 2025-11-19                    ║
╚══════════════════════════════════════════════════════════════╝

PURPOSE:
  Generate client invoices with automated pricing and calculations

INSTRUCTIONS:
  1. Enter client info in cells B1:E1
  2. Enter menu items in column A (starting row 3)
  3. Enter quantities in column C
  4. Prices auto-populate from lookup table (F:G)
  5. Totals calculate automatically

FORMULAS:
  - Column B: =IFNA(VLOOKUP(A3,$F$2:$G$100,2,FALSE),"")
  - Column D: =B3*C3
  - Cell D27: =SUM(D3:D25)
  - Cell D28: =D27*0.0815  (Tax)
  - Cell D29: =D27*0.20    (Service Fee)

IMPORTANT NOTES:
  - Do NOT delete rows 2-26 (formula range)
  - Do NOT modify columns F:G (price lookup table)
  - Save as new file for each client (don't overwrite template)

TROUBLESHOOTING:
  - #N/A error: Item name doesn't match price list exactly
  - #REF error: A referenced cell was deleted

VERSION HISTORY:
  v2.1 (2025-11-19): Added service fee calculation
  v2.0 (2025-11-15): Added IFNA error handling
  v1.0 (2025-11-01): Initial template
```

---

### Change Log Standard

**Keep a CHANGES.txt file or sheet:**
```
=====================================
LARIAT INVOICE TEMPLATE - CHANGE LOG
=====================================

2025-11-19 - v2.1
-----------------
ADDED:
  - Service fee calculation (20% of subtotal)
  - Minimum spend check

CHANGED:
  - Tax rate updated to 8.15% (was 8.0%)
  - Price lookup table expanded to 100 rows

FIXED:
  - #N/A errors now show blank instead
  - Subtotal formula now excludes empty rows

2025-11-15 - v2.0
-----------------
ADDED:
  - IFNA error handling on all VLOOKUP formulas

CHANGED:
  - Improved formula efficiency

2025-11-01 - v1.0
-----------------
  - Initial release
```

---

## 4️⃣ USING CLAUDE FOR CODING {#using-claude-for-coding}

### How to Get Best Results from Claude

#### 1. Be Specific with Requests

**❌ BAD:**
> "Help me with Excel formulas"

**✅ GOOD:**
> "I need an Excel formula that looks up item names in column A against a price table in columns F:G, returns the price in column B, and shows blank (not #N/A) if the item isn't found"

---

#### 2. Provide Context

**Include:**
- What you're trying to accomplish
- Current state of your file/code
- What you've already tried
- Any error messages
- Relevant formulas/code snippets

**Example:**
> "I have an invoice template with items in column A and prices that should auto-populate in column B using VLOOKUP. My price table is in F2:G100. Currently getting #N/A errors when items aren't in the price list. How do I show blank instead?"

---

#### 3. Ask for Explanations
```
"Can you explain this formula line by line:
=IFNA(VLOOKUP(A3,$F$2:$G$100,2,FALSE),"")

I want to understand what each part does."
```

Claude will break it down so you can learn and modify later.

---

#### 4. Request Multiple Options
```
"Show me 3 different ways to calculate a 20% service fee in Excel:
1. Using simple formula
2. Using a cell reference for the percentage
3. Using a named range"
```

This helps you pick the best approach for your needs.

---

#### 5. Ask for Testing/Validation
```
"Here's my VBA code to copy data between sheets. Can you:
1. Check for potential errors
2. Suggest improvements
3. Add error handling
4. Add comments"
```

---

#### 6. Iterate and Refine

Start broad, then get specific:

1. "I need to automate invoice creation"
2. Claude provides general approach
3. "Can you show me the exact formula for cell B3?"
4. Claude provides formula
5. "What if I want to handle items not in the price list?"
6. Claude adds error handling

---

### Code Generation Prompts

**For Excel Formulas:**
```
Create an Excel formula that:
- [What it should do]
- [Input location]
- [Output location]
- [Special conditions]
- [Error handling needed]
```

**For VBA:**
```
Write VBA code that:
- [Task to accomplish]
- [Trigger/when it runs]
- [What sheets/ranges involved]
- [Error handling requirements]
- Include comments explaining the code
```

**For Documentation:**
```
Create documentation for this [formula/code]:
- What it does
- How to use it
- What could go wrong
- How to troubleshoot
```

---

## 5️⃣ VERSION CONTROL BEST PRACTICES {#version-control}

### File Naming Convention
```
[Template]_[Client]_[Date]_v[#].xlsx

Examples:
Invoice_Template_v2.1.xlsx                (Master template)
Invoice_KaitlynTori_2025-10-17_v1.xlsx    (Client copy)
Invoice_KaitlynTori_2025-10-17_v2.xlsx    (After revisions)
```

**Rules:**
- Never overwrite master template
- Increment version number for each revision
- Include date in ISO format (YYYY-MM-DD)
- Use underscores (not spaces)

---

### Version Incrementation

**Major Version (v1.0 → v2.0):**
- Significant formula changes
- Added/removed sheets
- Structural changes
- Breaking changes

**Minor Version (v2.0 → v2.1):**
- Small formula improvements
- Added features
- Bug fixes
- Non-breaking changes

**Patch (v2.1 → v2.1.1):**
- Typo fixes
- Minor tweaks
- No functional changes

---

### Backup Strategy

**Daily:**
- Save working files to cloud (Google Drive, OneDrive, Dropbox)
- Enable auto-save if available

**Weekly:**
- Copy active projects to external drive
- Zip completed events to archive

**Monthly:**
- Full system backup
- Test restore process (make sure backups actually work!)

---

## 6️⃣ TESTING & QUALITY ASSURANCE {#testing-qa}

### Formula Testing Checklist

**Before deploying any formula:**

- [ ] Test with normal values
- [ ] Test with zero
- [ ] Test with negative numbers (if applicable)
- [ ] Test with blank cells
- [ ] Test with text in number fields
- [ ] Test with very large numbers
- [ ] Test with very small numbers
- [ ] Test edge cases (minimum, maximum values)
- [ ] Check error handling (#N/A, #DIV/0!, etc.)
- [ ] Verify absolute vs relative references

---

### Template Testing Process

**1. Create Test Invoice:**
```
Client: TEST_CLIENT
Date: Today
Items: Mix of real menu items and invalid items
Quantities: Include 0, 1, 100, and fractional amounts
```

**2. Verify Calculations:**
- Check each formula result manually
- Verify subtotal = sum of line items
- Verify tax = subtotal × 0.0815
- Verify service fee = subtotal × 0.20
- Verify total = subtotal + tax + service fee

**3. Test Error Conditions:**
- Enter item not in price list (should show blank, not error)
- Delete a referenced cell (should show #REF!, fix it)
- Enter text in quantity field (should show #VALUE!, add validation)

**4. Test Kitchen Sheet:**
- Verify items auto-populate from invoice
- Verify quantities copy correctly
- Test with 0 items, 10 items, 25 items

---

### VBA Testing

#### 1. Unit Testing:
Test each procedure individually
```vb
Sub TestUpdateKitchenSheet()
    ' Set up test data
    Sheets("Invoice").Range("A3").Value = "Test Item"
    Sheets("Invoice").Range("C3").Value = 10

    ' Run procedure
    UpdateKitchenSheet

    ' Verify result
    If Sheets("Kitchen Sheet").Range("A3").Value = "Test Item" Then
        MsgBox "Test PASSED", vbInformation
    Else
        MsgBox "Test FAILED", vbCritical
    End If
End Sub
```

#### 2. Integration Testing:
Test full workflow end-to-end

#### 3. Error Testing:
Try to break it:
- Run with empty sheets
- Run with invalid data
- Run multiple times in a row
- Verify error handler catches issues

---

## 7️⃣ AUTOMATION & SCRIPTING {#automation-scripting}

### Python for Excel Automation

**When to Use Python:**
- Batch processing multiple files
- Complex data transformations
- Integration with other systems
- Advanced reporting

**Basic Template:**
```python
import openpyxl
from pathlib import Path

def process_invoice(file_path):
    """
    Process a single invoice file
    """
    # Load workbook
    wb = openpyxl.load_workbook(file_path)
    ws = wb['Invoice']

    # Read data
    client_name = ws['B1'].value
    event_date = ws['C1'].value

    # Process...
    # (Your logic here)

    # Save
    wb.save(file_path)
    print(f"Processed: {file_path}")

def batch_process():
    """
    Process all invoice files in a directory
    """
    invoice_dir = Path('active_events')

    for file in invoice_dir.glob('Invoice_*.xlsx'):
        try:
            process_invoice(file)
        except Exception as e:
            print(f"Error processing {file}: {e}")

if __name__ == '__main__':
    batch_process()
```

---

### Useful Python Libraries

**For Excel:**
- `openpyxl` - Read/write .xlsx files
- `xlwings` - Python + Excel integration (can run formulas, use VBA)
- `pandas` - Data analysis and manipulation

**For PDFs:**
- `reportlab` - Generate PDFs from scratch
- `pypdf` - Manipulate existing PDFs

**For Automation:**
- `schedule` - Schedule tasks
- `smtplib` - Send emails automatically

---

## 8️⃣ NAMING CONVENTIONS {#naming-conventions}

### Cell Names (Named Ranges)
```
Tax_Rate = $H$2
Service_Fee_Pct = $H$3
Price_Lookup_Table = $F$2:$G$100
Invoice_Items = $A$3:$E$25
```

**Benefits:**
- `=D27*Tax_Rate` is clearer than `=D27*$H$2`
- If you move cells, formulas still work
- Easier to maintain

**To Create:**
1. Select cell or range
2. Click name box (left of formula bar)
3. Type name (no spaces, use underscores)
4. Press Enter

---

### Sheet Names

**Good:**
- Invoice
- Kitchen_Sheet
- Price_Lookup
- Client_Info

**Bad:**
- Sheet1
- Sheet2
- Data
- Temp

**Rules:**
- Descriptive and specific
- Use underscores (not spaces)
- Keep relatively short

---

### File Names

Already covered in Version Control, but recap:
```
[Type]_[Identifier]_[Date]_v[#].[ext]

Invoice_Template_v2.1.xlsx
KitchenSheet_McMahon_2025-07-18_v1.xlsx
ProductionSchedule_Logan_2025-09-18_v3.xlsx
```

---

## 9️⃣ FILE ORGANIZATION {#file-organization}

### Directory Structure
```
LARIAT_BANQUET_SYSTEM/
│
├── 📁 TEMPLATES/
│   ├── Invoice_Template_v2.1.xlsx
│   ├── Kitchen_Sheet_Template_v1.5.xlsx
│   ├── Production_Schedule_Template_v1.0.xlsx
│   └── README.txt
│
├── 📁 ACTIVE_EVENTS/
│   ├── 📁 KaitlynTori_2025-10-17/
│   │   ├── Invoice_KaitlynTori_2025-10-17_v1.xlsx
│   │   ├── Invoice_KaitlynTori_2025-10-17_v2.xlsx (final)
│   │   ├── KitchenSheet_KaitlynTori_2025-10-17_v1.xlsx
│   │   └── NOTES.txt
│   │
│   └── 📁 Logan_2025-09-18/
│       └── (similar structure)
│
├── 📁 COMPLETED_EVENTS/
│   └── 📁 2025/
│       └── 📁 October/
│           └── KaitlynTori_2025-10-17/ (archived)
│
├── 📁 REFERENCE/
│   ├── Lariat_Recipe_Book.docx
│   ├── LARIAT_ORDER_GUIDE_OFFICIAL.xlsx
│   └── LARIAT_INGREDIENTS_MASTER.xlsx
│
├── 📁 DOCUMENTATION/
│   ├── PROJECT_RULES.md
│   ├── WORKFLOW.md
│   ├── SYSTEM_OVERVIEW.md
│   └── QA_CUSTOMIZATION_GUIDE.md
│
└── 📁 BACKUPS/
    ├── 📁 Daily/
    ├── 📁 Weekly/
    └── 📁 Monthly/
```

---

### File Organization Rules

**1. Never Work in TEMPLATES folder:**
- Always copy to ACTIVE_EVENTS first
- Templates are read-only reference

**2. One Client = One Folder:**
- All files for an event in one place
- Easy to find everything

**3. Archive Completed Events:**
- Move to COMPLETED_EVENTS after 30 days
- Organize by year/month
- Compress to save space

**4. Regular Cleanup:**
- Delete old test files
- Remove duplicate versions
- Clear old backups (keep last 3 months)

---

## 🔟 TROUBLESHOOTING & DEBUGGING {#troubleshooting}

### Excel Formula Debugging

**Step 1: Check the Formula:**
- Click cell with error
- Look at formula bar
- Read formula left to right

**Step 2: Evaluate Parts:**
- Use "Evaluate Formula" tool (Formulas tab → Evaluate Formula)
- Steps through formula piece by piece
- Shows what each part evaluates to

**Step 3: Check References:**
- Are ranges correct?
- Absolute vs relative references correct?
- Are referenced cells what you expect?

**Step 4: Test with Simple Data:**
- Create a test with known result
- If test works, problem is with data
- If test fails, problem is with formula

---

### Common Excel Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Formula not calculating | Calculation set to manual | Formulas tab → Calculation → Automatic |
| Number shows as text | Leading apostrophe or text format | Convert to number format, re-enter |
| Circular reference warning | Formula refers to itself | Find circular reference, break the loop |
| Slow workbook | Too many volatile formulas | Replace NOW(), TODAY() with values |
| #NAME? error | Typo in formula | Check spelling of function names |

---

### VBA Debugging

**Use Debug Tools:**
```vb
' Set breakpoints (click in gray margin next to line)
' Code pauses when it hits breakpoint
' Use F8 to step through line by line
' Hover over variables to see values

Sub MyProcedure()
    Dim x As Integer
    x = 10                ' Set breakpoint here
    Debug.Print x         ' Outputs to Immediate Window (Ctrl+G)
    MsgBox x
End Sub
```

**Debug.Print is Your Friend:**
```vb
Debug.Print "Starting procedure..."
Debug.Print "rowCounter = " & rowCounter
Debug.Print "clientName = " & clientName
```
View output in Immediate Window (Ctrl+G in VBA editor)

---

### Error Messages Decoded

**#N/A:**
- "Not Available"
- VLOOKUP couldn't find the value
- Check that lookup value matches table exactly (spelling, spaces, case)

**#REF!:**
- "Reference"
- Formula refers to a cell that was deleted
- Find the formula, fix the reference

**#VALUE!:**
- Wrong type of data
- Example: Trying to multiply text by a number
- Check data types

**#DIV/0!:**
- Dividing by zero
- Add check: `=IF(B1=0,"",A1/B1)`

**#NUM!:**
- Number problem
- Example: SQRT of negative number
- Check your math

**#NAME?:**
- Excel doesn't recognize something
- Usually a typo in function name
- Check spelling

---

### When to Ask for Help

**Before asking Claude or colleagues:**
- ✅ Try to fix it yourself (learn more this way)
- ✅ Google the error message
- ✅ Check documentation
- ✅ Test with simpler data

**When asking for help, provide:**
- Exact error message
- What you were trying to do
- What you've already tried
- Relevant formulas/code
- Sample data (if possible)

---

## 📚 QUICK REFERENCE

### Formula Quick Reference
```excel
' Price Lookup
=IFNA(VLOOKUP(A3,$F$2:$G$100,2,FALSE),"")

' Line Total
=B3*C3

' Subtotal
=SUM(D3:D25)

' Tax (8.15%)
=D27*0.0815

' Service Fee (20%)
=D27*0.20

' Grand Total
=SUM(D27:D29)

' Check Minimum Spend
=E33-D27
```

---

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Edit cell | F2 |
| Insert function | Shift+F3 |
| Evaluate formula | Alt+M,V,E |
| Show formulas | Ctrl+` |
| Fill down | Ctrl+D |
| Fill right | Ctrl+R |
| Name range | Ctrl+F3 |
| Find/Replace | Ctrl+F / Ctrl+H |
| VBA Editor | Alt+F11 |
| Immediate Window (VBA) | Ctrl+G |

---

### Excel Functions Reference

**Lookup:**
- `VLOOKUP(lookup_value, table, column, [exact])` - Vertical lookup
- `XLOOKUP(lookup, array, return)` - Modern lookup (Excel 365+)
- `INDEX(array, row, col)` - Return value at position
- `MATCH(lookup, array, [type])` - Find position of value

**Math:**
- `SUM(range)` - Add numbers
- `AVERAGE(range)` - Average of numbers
- `ROUND(number, digits)` - Round number
- `INT(number)` - Round down to integer
- `MOD(number, divisor)` - Remainder after division

**Logic:**
- `IF(condition, true_value, false_value)` - Conditional
- `AND(condition1, condition2, ...)` - All must be true
- `OR(condition1, condition2, ...)` - Any must be true
- `IFERROR(value, value_if_error)` - Error handling
- `IFNA(value, value_if_na)` - #N/A error handling

**Text:**
- `CONCATENATE(text1, text2, ...)` or `&` - Join text
- `LEFT(text, num_chars)` - Left characters
- `RIGHT(text, num_chars)` - Right characters
- `MID(text, start, length)` - Middle characters
- `TRIM(text)` - Remove extra spaces
- `UPPER(text)` / `LOWER(text)` - Change case

**Date/Time:**
- `TODAY()` - Current date
- `NOW()` - Current date/time
- `DATE(year, month, day)` - Create date
- `YEAR(date)` / `MONTH(date)` / `DAY(date)` - Extract parts

---

## 🎯 GOLDEN RULES

### The 10 Commandments of Coding

1. **Comment your code** - Future you will thank present you
2. **Test before deploying** - Better to find bugs yourself
3. **Use meaningful names** - `clientName` beats `x`
4. **Handle errors gracefully** - Don't let users see ugly errors
5. **Keep it simple** - Complexity is the enemy of reliability
6. **Document everything** - Write it down before you forget
7. **Version your files** - Never overwrite the only copy
8. **Back up regularly** - Hard drives fail
9. **Learn from mistakes** - Document what went wrong and how you fixed it
10. **Ask for help** - Nobody knows everything

---

## 🚀 NEXT STEPS

To implement these guidelines:

1. ✅ Save this document in your DOCUMENTATION folder
2. 📖 Review before coding - Refer back when stuck
3. 🎯 Start small - Apply one principle at a time
4. 💪 Practice - The more you use these standards, the more natural they become
5. 📝 Update - Add your own learnings as you go

---

## 📞 USING THIS GUIDE WITH CLAUDE

When asking Claude for help, you can reference this guide:

**"Per my Claude Code Guidelines, I need [task]. Please follow the [specific section] standards."**

**Examples:**
- "Per my Excel Formula Standards, create a VLOOKUP with error handling"
- "Per my VBA Coding Standards, write a procedure with proper comments and error handling"
- "Per my Documentation Standards, create a README for this template"

This ensures Claude's responses match your established conventions!

---

**Document Version:** 1.0
**Created:** November 19, 2025
**For:** Personal Reference - Lariat Banquet System
**Keep Updated:** Add learnings and refinements as you go
