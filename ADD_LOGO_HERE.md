# 🎨 Add Your Logo Here!

## The logo file is ready to use - just needs to be added!

### Your logo file location:
**On your computer:** `Downloads/whitelariatlogoblkbg.heic`

### Where it needs to go:
**In this project:** `static/images/lariat-logo-white.png`

---

## ✅ STEP-BY-STEP INSTRUCTIONS:

### Step 1: Convert HEIC to PNG

**On Mac (easiest):**
1. Find `whitelariatlogoblkbg.heic` in your Downloads folder
2. Double-click to open in Preview
3. Click: **File** → **Export**
4. Change **Format** to: **PNG**
5. Save as: `lariat-logo-white.png`

**OR use online converter:**
1. Go to: https://convertio.co/heic-png/
2. Upload: `whitelariatlogoblkbg.heic`
3. Download the converted PNG
4. Rename to: `lariat-logo-white.png`

### Step 2: Add to Project

Copy the PNG file to this location:
```
lariat-bible/static/images/lariat-logo-white.png
```

**Full path:**
```
/home/user/lariat-bible/static/images/lariat-logo-white.png
```

### Step 3: Verify

1. Check the file is in place:
   ```bash
   ls -lh static/images/lariat-logo-white.png
   ```

2. Start the app:
   ```bash
   python app.py
   ```

3. Open browser and visit: http://localhost:5000

4. Your logo should appear in the top-left navigation bar! 🎉

---

## 🔄 Alternative: Use the Conversion Script

If you can access the terminal on your local machine:

```bash
# Copy HEIC file to project
cp ~/Downloads/whitelariatlogoblkbg.heic /home/user/lariat-bible/

# Convert it
cd /home/user/lariat-bible
python convert_logo.py whitelariatlogoblkbg.heic

# Done!
```

---

## ❓ Troubleshooting

**Logo not showing?**
- File must be named exactly: `lariat-logo-white.png`
- File must be in: `static/images/` folder
- Refresh browser (Cmd+Shift+R or Ctrl+F5)

**File in wrong format?**
- Must be PNG, not HEIC
- Use Preview or online converter

**Still seeing cowboy icon?**
- That's the fallback - it means PNG file not found yet
- Double-check the file path and name

---

## 📁 Quick Reference

| Item | Value |
|------|-------|
| Source file | `~/Downloads/whitelariatlogoblkbg.heic` |
| Target file | `static/images/lariat-logo-white.png` |
| Target format | PNG with transparency |
| Recommended size | 200px width or larger |

---

**STATUS:** ⏳ Waiting for PNG file to be added

Once the PNG is in place, your logo will automatically appear on all pages!
