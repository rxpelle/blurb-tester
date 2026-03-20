# PDF Creation Instructions for The Aethelred Cipher

## Prerequisites

You need to install **pandoc** and **LaTeX** (for PDF generation).

### Installation Options:

**Option 1: Using Homebrew (Recommended)**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install pandoc
brew install pandoc

# Install BasicTeX (smaller LaTeX distribution, ~100MB)
brew install --cask basictex

# After installing BasicTeX, update PATH (add to ~/.zshrc or ~/.bash_profile)
export PATH="/Library/TeX/texbin:$PATH"

# Install additional LaTeX packages needed
sudo tlmgr update --self
sudo tlmgr install collection-fontsrecommended
```

**Option 2: Using MacPorts**
```bash
sudo port install pandoc
sudo port install texlive-basic
```

**Option 3: Direct Download**
- Download pandoc from: https://github.com/jgm/pandoc/releases
- Download MacTeX from: https://www.tug.org/mactex/

---

## PDF Generation Commands

Once pandoc is installed, navigate to the medieval v3 folder and run:

### Basic PDF (Simple formatting)
```bash
cd "/Users/randypellegrini/Documents/antigravity/plague_novel/medieval/medieval v3"

pandoc "The_Aethelred_Cipher_Book1_COMPLETE_PAGEBREAKS.md" \
  -o "The_Aethelred_Cipher_Book1.pdf" \
  --pdf-engine=pdflatex \
  --toc \
  --toc-depth=1 \
  -V documentclass=book \
  -V papersize=letter \
  -V geometry:margin=1in
```

### Professional PDF (Enhanced formatting)
```bash
pandoc "The_Aethelred_Cipher_Book1_COMPLETE_PAGEBREAKS.md" \
  -o "The_Aethelred_Cipher_Book1_FORMATTED.pdf" \
  --pdf-engine=pdflatex \
  --toc \
  --toc-depth=1 \
  -V documentclass=book \
  -V papersize=letter \
  -V geometry:margin=1in \
  -V fontsize=12pt \
  -V linestretch=1.5 \
  -V mainfont="Times New Roman" \
  --number-sections
```

### Premium PDF (Book-style formatting)
```bash
pandoc "The_Aethelred_Cipher_Book1_COMPLETE_PAGEBREAKS.md" \
  -o "The_Aethelred_Cipher_Book1_PREMIUM.pdf" \
  --pdf-engine=pdflatex \
  --toc \
  --toc-depth=2 \
  -V documentclass=book \
  -V papersize=letter \
  -V geometry:margin=1.25in \
  -V fontsize=11pt \
  -V linestretch=1.3 \
  -V linkcolor=blue \
  -V urlcolor=blue \
  -V toccolor=black \
  --number-sections \
  --highlight-style=tango
```

---

## Alternative: HTML to PDF (No pandoc required)

If you prefer not to install pandoc, you can create an HTML version and print to PDF from your browser:

```bash
# This uses Python (already installed on macOS)
cd "/Users/randypellegrini/Documents/antigravity/plague_novel/medieval/medieval v3"

# Create HTML version
python3 -c "
import markdown
import sys

with open('The_Aethelred_Cipher_Book1_COMPLETE.md', 'r') as f:
    text = f.read()

html = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <title>The Aethelred Cipher - Book 1</title>
    <style>
        @page { margin: 1in; }
        body {
            font-family: Georgia, serif;
            font-size: 12pt;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            page-break-before: always;
            font-size: 24pt;
            margin-top: 40px;
        }
        h1:first-of-type {
            page-break-before: avoid;
        }
        h2 { font-size: 18pt; }
        h3 { font-size: 14pt; }
        p { text-align: justify; }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
        }
        blockquote {
            border-left: 3px solid #ccc;
            padding-left: 15px;
            margin-left: 0;
        }
    </style>
</head>
<body>
''' + markdown.markdown(text, extensions=['extra', 'nl2br']) + '''
</body>
</html>
'''

with open('The_Aethelred_Cipher_Book1.html', 'w') as f:
    f.write(html)

print('HTML file created: The_Aethelred_Cipher_Book1.html')
" 2>/dev/null || echo "markdown package not installed. Install with: pip3 install markdown"
```

Then open the HTML file in your browser and use **File → Print → Save as PDF**.

---

## Quick Start (Recommended)

The easiest approach:

1. Install pandoc and BasicTeX using Homebrew (commands above)
2. Run the "Basic PDF" command
3. Result: `The_Aethelred_Cipher_Book1.pdf`

The file `The_Aethelred_Cipher_Book1_COMPLETE_PAGEBREAKS.md` has already been prepared with page breaks before each chapter.

---

## Files Available

- `The_Aethelred_Cipher_Book1_COMPLETE.md` - Original combined file
- `The_Aethelred_Cipher_Book1_COMPLETE_PAGEBREAKS.md` - With page breaks for PDF generation ✓

---

## Troubleshooting

**"pandoc: command not found"**
- Pandoc is not installed. Follow installation instructions above.

**"pdflatex not found"**
- LaTeX is not installed. Install BasicTeX or MacTeX.

**"Package X not found"**
- Run: `sudo tlmgr install [package-name]`

**PDF looks poorly formatted**
- Try the "Professional PDF" or "Premium PDF" commands for better formatting.

---

## Expected Result

A professionally formatted PDF with:
- Title page with author name
- Table of contents
- Each chapter starting on a new page
- Proper page numbers
- ~70,000 words across ~250-300 pages (depending on formatting)
