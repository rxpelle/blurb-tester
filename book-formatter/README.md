# Book Formatter

One command to format your book for every platform. Free, open-source book formatting for indie authors.

Replaces Vellum ($250) and Atticus ($150).

## Features

- **Paperback PDF** — KDP-ready interior with proper trim sizes, gutters, running headers
- **Large Print PDF** — 16pt body text, wider margins
- **Hardcover PDF** — Adjusted trim for case laminate
- **EPUB 3** — Clean, validated EPUB with cover and TOC
- Markdown manuscript input (single file or chapter-per-file directory)
- YAML configuration (`book.yaml`)
- Scene break styling, drop caps, widows/orphans control
- Multiple trim sizes (5x8, 5.25x8, 5.5x8.5, 6x9, 7x10, 8.5x11)

## Requirements

- Python 3.9+
- [Pandoc](https://pandoc.org/) (for all formats)
- XeLaTeX (for PDF generation) — install via `brew install --cask mactex` or `apt install texlive-xetex`

## Quick Start

```bash
pip install book-formatter

# Create a config file
book-formatter init

# Edit book.yaml, then build all formats
book-formatter build

# Build specific format
book-formatter build --format paperback

# Validate manuscript
book-formatter validate
```

## Manuscript Structure

Organize chapters as numbered markdown files:

```
manuscript/
  01_THE_BEGINNING.md
  02_THE_MIDDLE.md
  03_THE_END.md
  04_EPILOGUE.md
```

Or use a single markdown file with `# Chapter` headings.

## Configuration

```yaml
title: "My Book"
author: "Author Name"
manuscript: "manuscript/"
output: "output/"
style: default

print:
  trim: "5.5x8.5"

typography:
  body_font: "EB Garamond"
  body_size: 11
  line_spacing: 1.15
```

## License

MIT
