# KDP FORMATTING WORKFLOW

**Last Updated**: January 24, 2026
**Purpose**: Ensure proper page breaks and formatting when converting to KDP

---

## ⚠️ CRITICAL: Always Use the Lua Filter

KDP requires proper Word page breaks, not HTML or LaTeX formatting. The standard pandoc conversion does NOT preserve page breaks correctly.

---

## Required Files

1. **Source**: `The Aethelred Cipher - Complete with Front Matter.md`
2. **Filter**: `pagebreak.lua` (download from https://raw.githubusercontent.com/pandoc/lua-filters/master/pagebreak/pagebreak.lua)
3. **Output**: `The Aethelred Cipher.docx`

---

## Markdown Formatting Rules

### ✅ CORRECT - Use LaTeX newpage commands:

```markdown
\newpage

# CHAPTER 1 - THE KEY {#chapter-1}
```

### ❌ INCORRECT - Don't use HTML divs:

```markdown
<div style="page-break-after: always;"></div>

# CHAPTER 1 - THE KEY
```

**Why**: The Lua filter converts `\newpage` to proper Word OOXML page breaks (`<w:br w:type="page"/>`). HTML divs don't translate correctly through pandoc.

---

## Table of Contents Links

### ✅ CORRECT - Clickable TOC with anchor links:

**In Table of Contents:**
```markdown
# Table of Contents

[**CHAPTER 1** - The Key](#chapter-1)

[**CHAPTER 2** - The Ghost](#chapter-2)
```

**Chapter Headings with Anchors:**
```markdown
# CHAPTER 1 - THE KEY {#chapter-1}

# CHAPTER 2 - THE GHOST {#chapter-2}
```

**Why**: KDP/Kindle converts these markdown links to functional navigation links that allow readers to jump directly to chapters from the Table of Contents.

---

## Image Formatting for KDP

### ⚠️ CRITICAL: CSS Styling Doesn't Work in KDP

HTML/CSS styling (borders, padding, background colors) in markdown **does not translate** to KDP/Kindle format. Just like page breaks, you need a different approach.

### ✅ CORRECT - Add styling to the image file itself:

**Step 1: Create bordered image with Python/Pillow:**
```bash
python3 << 'EOF'
from PIL import Image, ImageOps

# Open original image
img = Image.open('randypellegrini.jpg')

# Add white border (5px padding)
img_with_white = ImageOps.expand(img, border=5, fill='white')

# Add black border (3px)
img_with_borders = ImageOps.expand(img_with_white, border=3, fill='black')

# Save as new file
img_with_borders.save('randypellegrini_bordered.jpg', quality=95)
EOF
```

**Step 2: Use simple markdown syntax:**
```markdown
![Randy Pellegrini](randypellegrini_bordered.jpg){width=40%}
```

### ❌ INCORRECT - Don't use HTML/CSS styling:
```markdown
<div style="text-align: center;">
<img src="image.jpg" style="border: 3px solid black; padding: 5px;">
</div>
```

**Why**: KDP strips HTML/CSS during conversion to EPUB/MOBI. Borders and styling baked into the image file itself will display correctly on all Kindle devices.

---

## Conversion Command

**From the manuscript directory**, run:

```bash
pandoc "The Aethelred Cipher - Complete with Front Matter.md" \
  -o "The Aethelred Cipher.docx" \
  --lua-filter=pagebreak.lua
```

**Then copy to Google Drive**:

```bash
cp "The Aethelred Cipher.docx" \
  "/Users/randypellegrini/Library/CloudStorage/GoogleDrive-randypellegrini@gmail.com/My Drive/Black Plague Book/The Aethelred Cipher.docx"
```

---

## Verification

### Check page break count:

```bash
unzip -q -o "The Aethelred Cipher.docx" -d temp_docx
grep -o '<w:br w:type="page"/>' temp_docx/word/document.xml | wc -l
rm -rf temp_docx
```

**Expected result**: Should show 18-21 page breaks (one for each chapter + front matter sections)

### Visual verification:

1. Open DOCX in **Kindle Previewer 3**
2. Check that each chapter starts on a new page
3. Verify front matter sections are separated

---

## Common Issues

### Issue: Kindle Previewer shows no page breaks
**Cause**: Conversion was done without the Lua filter
**Fix**: Regenerate DOCX using the command above with `--lua-filter=pagebreak.lua`

### Issue: HTML tags visible in output
**Cause**: Used HTML divs instead of `\newpage` in markdown
**Fix**: Replace all `<div style="page-break-after: always;"></div>` with `\newpage`

### Issue: Filter not found
**Cause**: `pagebreak.lua` not in manuscript directory
**Fix**: Download from https://raw.githubusercontent.com/pandoc/lua-filters/master/pagebreak/pagebreak.lua

---

## Technical Details

### What the Lua filter does:

1. Detects `\newpage` or `\pagebreak` commands in markdown
2. Converts them to format-specific page breaks:
   - **DOCX/OOXML**: `<w:p><w:r><w:br w:type="page"/></w:r></w:p>`
   - **HTML/EPUB**: `<div style="page-break-after: always;"></div>`
   - **ODT**: `<text:p text:style-name="Pagebreak"/>`

### Why this matters for KDP:

- KDP's converter expects **native Word page breaks** in DOCX files
- HTML tags or manual spacing (repeated Enter keys) cause formatting issues
- Proper OOXML breaks translate cleanly to EPUB/MOBI for Kindle devices

---

## References

- [KDP eBook Manuscript Formatting Guide](https://kdp.amazon.com/en_US/help/topic/G200645680)
- [Pandoc Lua Filters - Pagebreak](https://github.com/pandoc/lua-filters/blob/master/pagebreak/README.md)
- [Pandoc Manual - Custom Writers](https://pandoc.org/MANUAL.html)
- [How to Format a Book for Amazon KDP (2026)](https://www.bookbloom.io/blog/how-to-format-book-amazon-kdp)

---

## Quick Reference

**Every time you update the manuscript and need to generate the DOCX:**

```bash
cd /Users/randypellegrini/Documents/antigravity/plague_novel/book_1_aethelred_cipher/manuscript

# Generate DOCX with proper page breaks
pandoc "The Aethelred Cipher - Complete with Front Matter.md" \
  -o "The Aethelred Cipher.docx" \
  --lua-filter=pagebreak.lua

# Copy to Google Drive
cp "The Aethelred Cipher.docx" \
  "/Users/randypellegrini/Library/CloudStorage/GoogleDrive-randypellegrini@gmail.com/My Drive/Black Plague Book/The Aethelred Cipher.docx"

# Verify page breaks
unzip -q -o "The Aethelred Cipher.docx" -d temp_docx && \
grep -o '<w:br w:type="page"/>' temp_docx/word/document.xml | wc -l && \
rm -rf temp_docx
```

**Expected output**: 18-21 page breaks

---

## File Structure

```
manuscript/
├── The Aethelred Cipher - Complete with Front Matter.md  ← Source (always use \newpage)
├── pagebreak.lua                                         ← Lua filter (required)
├── The Aethelred Cipher.docx                            ← Generated output
└── KDP_FORMATTING_WORKFLOW.md                           ← This file
```
