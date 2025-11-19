# Logo Setup Instructions

## Adding Your Logo

### Step 1: Convert HEIC to PNG/SVG
Since HEIC files aren't web-compatible, convert your logo:
- Use an online converter or Mac Preview app
- Export as PNG (with transparency) or SVG
- Recommended size: 200x200px or larger

### Step 2: Add Logo Files
Place your converted logo files in:
```
/home/user/lariat-bible/static/images/
```

Recommended files:
- `lariat-logo-white.png` - White logo for dark backgrounds (navbar)
- `lariat-logo-color.png` - Color logo for light backgrounds
- `lariat-logo.svg` - SVG version (scalable, best quality)

### Step 3: Logo is Already Integrated
The templates have been updated to use your logo. Just add the image files and refresh!

### Current Status
✅ Templates updated to use logo
✅ CSS styles prepared
✅ Fallback icon in place until logo is added
⏳ Waiting for logo file upload

## Quick Upload via Python Script

You can also use this Python script to convert and upload:

```python
from PIL import Image
import pillow_heif

# Convert HEIC to PNG
heif_file = pillow_heif.read_heif("whitelariatlogoblkbg.heic")
image = Image.frombytes(
    heif_file.mode,
    heif_file.size,
    heif_file.data,
    "raw",
)
image.save("static/images/lariat-logo-white.png", "PNG")
```

Or use ImageMagick:
```bash
convert whitelariatlogoblkbg.heic static/images/lariat-logo-white.png
```
