# Quick Reference Card
## Lariat Banquet System - Most Common Tasks

---

## 🔥 Excel Formulas - Copy & Paste Ready

### Price Lookup with Error Handling
```excel
=IFNA(VLOOKUP(A3,$F$2:$G$100,2,FALSE),"")
```

### Line Total (Price × Quantity)
```excel
=B3*C3
```

### Subtotal (Sum of Line Items)
```excel
=SUM(D3:D25)
```

### Tax Calculation (8.15%)
```excel
=D27*0.0815
```
**Better with cell reference:**
```excel
=D27*$H$2
```
*(Put 0.0815 in H2)*

### Service Fee (20%)
```excel
=D27*0.20
```
**Better with cell reference:**
```excel
=D27*$H$3
```
*(Put 0.20 in H3)*

### Grand Total
```excel
=SUM(D27:D29)
```

### Check if Over/Under Minimum
```excel
=E33-D27
```
*Positive = Over, Negative = Under*

---

## ⌨️ Excel Shortcuts

| Task | Shortcut |
|------|----------|
| Edit cell | **F2** |
| Insert function | **Shift + F3** |
| Show formulas | **Ctrl + `** |
| Fill down | **Ctrl + D** |
| Fill right | **Ctrl + R** |
| Find | **Ctrl + F** |
| Replace | **Ctrl + H** |
| VBA Editor | **Alt + F11** |

---

## 🎯 File Naming Convention

```
[Type]_[Client]_[Date]_v[#].xlsx

Examples:
- Invoice_Template_v2.1.xlsx
- Invoice_KaitlynTori_2025-10-17_v1.xlsx
- KitchenSheet_McMahon_2025-07-18_v1.xlsx
```

**Date Format:** YYYY-MM-DD
**Separator:** Underscores (not spaces)

---

## 🔍 Troubleshooting Common Errors

| Error | What It Means | Quick Fix |
|-------|---------------|-----------|
| **#N/A** | Lookup value not found | Wrap in `IFNA(...,"")` |
| **#REF!** | Referenced cell deleted | Check formula references |
| **#DIV/0!** | Dividing by zero | Add `IF(B3=0,"",A3/B3)` |
| **#VALUE!** | Wrong data type | Check numbers aren't text |
| **#NAME?** | Typo in formula | Check function spelling |

---

## 📋 Before Deploying a Formula

- [ ] Test with normal values
- [ ] Test with zero
- [ ] Test with blank cells
- [ ] Test with text in number fields
- [ ] Check error handling
- [ ] Verify absolute/relative references

---

## 🐍 Python Quick Import

```python
import openpyxl
from pathlib import Path

# Load workbook
wb = openpyxl.load_workbook('file.xlsx')
ws = wb['Sheet1']

# Read cell
value = ws['A1'].value

# Write cell
ws['A1'].value = "New Value"

# Save
wb.save('file.xlsx')
```

---

## 💬 Asking Claude for Help

### ✅ Good Prompt
```
I need an Excel formula that looks up item names in column A
against a price table in F2:G100, returns the price in column B,
and shows blank (not #N/A) if the item isn't found.

Per my Claude Code Guidelines section 1, please include error handling.
```

### ❌ Bad Prompt
```
Help me with Excel
```

---

## 🎯 The 3 Golden Rules

1. **Comment Everything** - Future you will thank you
2. **Test Before Deploy** - Find bugs yourself first
3. **Version Control** - Never overwrite the only copy

---

## 📞 Quick Links

- **Full Guidelines:** CLAUDE_CODE_GUIDELINES.md
- **Documentation Index:** DOCUMENT_INDEX.md
- **Project README:** ../README.md

---

**Print this page and keep it handy!**
**Version:** 1.0 | **Updated:** 2025-11-19
