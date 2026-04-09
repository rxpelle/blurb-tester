#!/usr/bin/env python3
"""Build combined manuscript for The First Key (Book 3).

Generates:
  1. DOCX source markdown (with HTML title page)
  2. PDF source markdown (title page via title.tex)
  3. Paperback PDF (5.5x8.5) via pandoc + xelatex
  4. EPUB via pandoc

Usage:
  python3 build_manuscript.py          # build markdown sources only
  python3 build_manuscript.py --pdf    # also build paperback PDF
  python3 build_manuscript.py --epub   # also build EPUB
  python3 build_manuscript.py --all    # build everything
"""

import os
import re
import glob
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(SCRIPT_DIR, '..')
CHAPTERS_V2 = os.path.join(PROJECT_DIR, 'chapters_v2')
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output')
OUTPUT_DOCX = os.path.join(SCRIPT_DIR, 'The First Key - Complete with Front Matter.md')
OUTPUT_PDF = os.path.join(SCRIPT_DIR, 'The First Key - PDF Source.md')

# Chapter titles for TOC (extracted from filenames)
CHAPTER_FILES = sorted(glob.glob(os.path.join(CHAPTERS_V2, '[0-1][0-9]_*.md')))

# =============================================================================
# BOOK METADATA (edit these for each book)
# =============================================================================
BOOK_TITLE = 'The First Key'
BOOK_TITLE_UPPER = 'THE FIRST KEY'
BOOK_NUMBER = 3
SERIES_NAME = 'The Architecture of Survival'
AUTHOR = 'Randy Pellegrini'
COPYRIGHT_YEAR = 2026
WEBSITE = 'randypellegrini.com'

# =============================================================================
# PAPERBACK PDF SETTINGS
# =============================================================================
PAPERBACK_SIZE = '5.5x8.5'  # KDP trim size
PAPERBACK_SETTINGS = {
    '5.5x8.5': {
        'paperwidth': '5.5in',
        'paperheight': '8.5in',
        'top': '0.75in',
        'bottom': '0.75in',
        'inner': '0.75in',    # gutter (spine side) — wider for binding
        'outer': '0.375in',   # outer edge — text closer to trim
    },
    '6x9': {
        'paperwidth': '6in',
        'paperheight': '9in',
        'top': '0.5in',
        'bottom': '0.5in',
        'inner': '0.625in',
        'outer': '0.5in',
    },
}
FONT_SIZE = '11pt'
FONT_FAMILY = 'Georgia'
LINE_STRETCH = '1.3'


# =============================================================================
# TITLE PROCESSING
# =============================================================================

def clean_title(filename):
    """Extract clean title from filename like 01_THE_PHYSICIANS_WITNESS.md"""
    base = os.path.basename(filename).replace('.md', '')
    num = base[:2]
    raw_title = base[3:]
    # Convert underscores to spaces and title case
    title = raw_title.replace('_', ' ').title()
    # Fix specific words
    title = title.replace('And', 'and')
    title = title.replace("'S", "'s")
    title = title.replace('Book4', 'Book 4')
    # Restore apostrophes lost in filename conventions
    title = title.replace('Physicians Witness', "Physician's Witness")
    title = title.replace('Physicians Rest', "Physician's Rest")
    title = title.replace('Kingdoms Healer', "Kingdom's Healer")
    title = title.replace('Academys Secret', "Academy's Secret")
    title = title.replace('Oracles Network', "Oracle's Network")
    title = title.replace('Philosophers Vision', "Philosopher's Vision")
    return int(num), title


def make_anchor(num, title):
    """Create anchor ID like #chapter-1"""
    if num == 14:
        return 'epilogue'
    return f'chapter-{num}'


# =============================================================================
# FRONT MATTER
# =============================================================================

def build_about_and_toc(chapters):
    """Build about author and TOC sections (shared by both outputs)."""
    lines = []

    # About the Author
    lines.append('# About the Author {.unnumbered}\n')
    lines.append(f'Randy Pellegrini writes *{SERIES_NAME}*, a 12-book epic spanning 3,200 years from Bronze Age Egypt to the modern era. The series explores genetic memory as hard science, civilizational collapse patterns, and the moral complexity of two competing philosophies: knowledge preservation versus genetic control.\n')
    lines.append('The saga weaves real historical events with speculative elements grounded in epigenetics, network theory, and systems thinking. Each book stands alone while revealing how defensive methodology has been embedded into human civilization through every era\'s dominant technology.\n')
    lines.append('When not writing, Randy travels near and far to better imagine history up close and personal. He continuously wonders why we continue to replay broken patterns of human systems. That wonder was the seed that has grown into this series.\n')
    lines.append(f'To learn more about the book series, visit [{WEBSITE}/series](https://{WEBSITE}/series)\n')
    lines.append('\n\\newpage\n')

    return '\n'.join(lines)


def build_docx_front_matter(chapters):
    """Build HTML title page + about author + TOC for DOCX output."""
    lines = []

    # HTML title page (renders well in DOCX)
    lines.append('\\newpage\n')
    lines.append('<p style="text-align: center; margin-top: 4cm;">')
    lines.append(f'<span style="font-size: 2.5em; font-weight: bold;">{BOOK_TITLE_UPPER}</span>')
    lines.append('</p>\n')
    lines.append('<p style="text-align: center; margin-top: 0.5cm;">')
    lines.append(f'<span style="font-size: 1.2em;">Book {BOOK_NUMBER} of {SERIES_NAME}</span>')
    lines.append('</p>\n')
    lines.append('<p style="text-align: center; margin-top: 2cm;">')
    lines.append(f'<span style="font-size: 1.5em;">{AUTHOR}</span>')
    lines.append('</p>\n')
    lines.append('<p style="text-align: center; margin-top: 3cm;">')
    lines.append('</p>\n')
    lines.append(f'[{WEBSITE}](https://{WEBSITE})\n')
    lines.append(f'Copyright \u00a9 {COPYRIGHT_YEAR} {AUTHOR}\n')
    lines.append('All rights reserved.\n')
    lines.append('No part of this book may be reproduced in any form or by any electronic or mechanical means, including information storage and retrieval systems, without written permission from the author, except for the use of brief quotations in a book review.\n')
    lines.append('This is a work of fiction. Names, characters, places, and incidents either are the product of the author\'s imagination or are used fictitiously. Any resemblance to actual persons, living or dead, events, or locales is entirely coincidental.\n')
    lines.append('\n\\newpage\n')

    # About author
    lines.append(build_about_and_toc(chapters))

    # Manual TOC for DOCX
    lines.append('# Table of Contents\n')
    for filepath in chapters:
        num, title = clean_title(filepath)
        anchor = make_anchor(num, title)
        if num == 14:
            lines.append(f'[**EPILOGUE** - The Gathering](#{anchor})\n')
        else:
            lines.append(f'[**CHAPTER {num}** - {title}](#{anchor})\n')

    lines.append('\n\\newpage\n')

    return '\n'.join(lines)


def build_pdf_front_matter(chapters):
    """Build front matter for PDF (title page handled by title.tex)."""
    lines = []

    # About author (title page comes from title.tex via --include-before-body)
    lines.append(build_about_and_toc(chapters))

    return '\n'.join(lines)


# =============================================================================
# CHAPTER PROCESSING
# =============================================================================

def process_chapter(filepath):
    """Read a chapter file and clean it for the combined manuscript."""
    with open(filepath, 'r') as f:
        content = f.read()

    num, title = clean_title(filepath)
    anchor = make_anchor(num, title)

    # Remove END CHAPTER / END OF BOOK markers and any surrounding ---
    content = re.sub(r'\n+\*?\*?---\*?\*?\s*\n+\*?\*?END CHAPTER \d+\*?\*?\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n+---\s*\n+\*?\*?END CHAPTER \d+\*?\*?\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n+\*?\*?---?\*?\*?\s*\n+\*?\*?END OF BOOK.*$', '', content, flags=re.MULTILINE | re.DOTALL)
    content = re.sub(r'\*\*END OF BOOK.*$', '', content, flags=re.MULTILINE | re.DOTALL)

    # Remove CONTINUITY NOTES / EPILOGUE NOTES sections (editorial working notes, not for publication)
    content = re.sub(
        r'\n+(?:##?\s*)?(?:\*\*)?(?:CHAPTER \d+ )?(?:CONTINUITY|EPILOGUE) NOTES:?\*?\*?\s*\n.*',
        '', content, flags=re.DOTALL
    )

    # Replace ## SCENE X: labels with scene break markers
    # First remove any --- that directly precedes a SCENE heading (avoids double breaks)
    content = re.sub(r'\n---\n+(?=## SCENE \d+)', '\n', content)
    content = re.sub(r'^## SCENE \d+.*$', '---', content, flags=re.MULTILINE)

    # Collapse any consecutive --- markers (even with blank lines between) into a single one
    content = re.sub(r'---\s*\n(\s*\n)*\s*---', '---', content)

    # Fix setext heading bug: ensure blank line before every --- separator
    content = re.sub(r'([^\n])\n---', r'\1\n\n---', content)

    # Remove duplicate subtitle lines like "## CHAPTER 1: THE PHYSICIAN'S WITNESS" or ## "The Title"
    content = re.sub(r'^## CHAPTER \d+:.*$\n?', '', content, flags=re.MULTILINE)
    content = re.sub(r'^## ".*"$\n?', '', content, flags=re.MULTILINE)

    # Remove stray --- that appears right after the chapter header (between title and first content)
    content = re.sub(r'(^# .+\n)\n*---\n', r'\1\n', content, flags=re.MULTILINE)

    # Replace the original header with just the title (no "CHAPTER N" prefix — LaTeX handles numbering)
    # Source headers vary: "# BOOK 3: THE FIRST KEY - CHAPTER N", "# BOOK 3: CHAPTER 1 - THE COLLAPSE", etc.
    if num == 14:
        content = re.sub(
            r'^# .*EPILOGUE.*$',
            f'# The Gathering {{#{anchor}}}',
            content, count=1, flags=re.MULTILINE
        )
    else:
        content = re.sub(
            r'^# BOOK 3:.*$',
            f'# {title} {{#{anchor}}}',
            content, count=1, flags=re.MULTILINE
        )

    # Move date/place line above the scene-break bar (swap --- and **date** order)
    content = re.sub(
        r'\n---\n\n(\*\*[^*]+\*\*)',
        r'\n\1\n\n---',
        content, count=1
    )

    return content.rstrip() + '\n'


# =============================================================================
# BACK MATTER
# =============================================================================

def build_back_matter():
    """Build the end-of-book section."""
    lines = []
    lines.append('\n\\newpage\n')
    lines.append('* * *\n')
    lines.append('**Continue reading in Book 4: THE PROPHET\'S BURDEN**\n')
    lines.append('One thousand years after Nefertari created the Genesis Protocol, a carpenter\'s son in Galilee carries Generation 41 of the bloodline \u2014 and his teachings will reshape the network\'s mission for two millennia.\n')
    lines.append(f'For more information on the books in this series and to better understand the meaning behind the concepts these books elicit, go to the author\'s webpage [{WEBSITE}/series](https://{WEBSITE}/series).\n')
    lines.append('Looking forward to your feedback and correspondence,\n')
    lines.append(f'{AUTHOR}\n')
    lines.append('\n\\newpage\n')
    return '\n'.join(lines)


# =============================================================================
# BUILD COMBINED CHAPTERS
# =============================================================================

def build_chapters_and_back():
    """Build chapter content and back matter (shared by both outputs)."""
    parts = []
    for i, filepath in enumerate(CHAPTER_FILES):
        num, title = clean_title(filepath)
        print(f"  Processing: Chapter {num} - {title}")

        if i > 0:
            parts.append('\n\\newpage\n\n\\newpage\n')

        chapter_content = process_chapter(filepath)
        parts.append(chapter_content)

    parts.append(build_back_matter())
    return parts


# =============================================================================
# PDF BUILD (pandoc + xelatex)
# =============================================================================

def build_paperback_pdf(size=None):
    """Build paperback PDF using pandoc + xelatex.

    Args:
        size: Trim size string like '5.5x8.5' or '6x9'. Defaults to PAPERBACK_SIZE.
    """
    size = size or PAPERBACK_SIZE
    settings = PAPERBACK_SETTINGS[size]
    size_label = size.replace('x', 'x')
    output_file = os.path.join(OUTPUT_DIR, f'The_First_Key_paperback_{size_label.replace("x", "x")}.pdf')

    geometry = f"paperwidth={settings['paperwidth']},paperheight={settings['paperheight']},top={settings['top']},bottom={settings['bottom']},inner={settings['inner']},outer={settings['outer']}"

    cmd = [
        'pandoc', OUTPUT_PDF,
        '-o', output_file,
        '--pdf-engine=xelatex',
        f'--include-in-header={os.path.join(SCRIPT_DIR, "header.tex")}',
        f'--include-before-body={os.path.join(SCRIPT_DIR, "title.tex")}',
        f'--lua-filter={os.path.join(SCRIPT_DIR, "pagebreak.lua")}',
        f'-V', f'geometry:{geometry}',
        '-V', f'fontsize={FONT_SIZE}',
        '-V', 'documentclass=book',
        '-V', 'classoption=openright',
        '-V', f'mainfont={FONT_FAMILY}',
        '-V', f'linestretch={LINE_STRETCH}',
        '--toc',
        '--toc-depth=1',
        '-V', 'toc-title=Contents',
    ]

    print(f"\nBuilding paperback PDF ({size})...")
    print(f"  Output: {os.path.basename(output_file)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    if result.stderr:
        # Print warnings but don't fail
        for line in result.stderr.strip().split('\n'):
            print(f"  Warning: {line}")
    print(f"  Done: {os.path.basename(output_file)}")
    return True


# =============================================================================
# EPUB BUILD
# =============================================================================

def build_epub():
    """Build EPUB using pandoc."""
    output_file = os.path.join(OUTPUT_DIR, 'The_First_Key_ebook.epub')
    cover_image = os.path.join(PROJECT_DIR, 'covers', 'first-key-cover-FINAL.png')

    cmd = [
        'pandoc', OUTPUT_PDF,
        '-o', output_file,
        f'--metadata=title:{BOOK_TITLE}',
        f'--metadata=author:{AUTHOR}',
        '--toc',
        '--toc-depth=1',
    ]

    # Add cover if it exists
    if os.path.exists(cover_image):
        cmd.append(f'--epub-cover-image={cover_image}')

    print(f"\nBuilding EPUB...")
    print(f"  Output: {os.path.basename(output_file)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    print(f"  Done: {os.path.basename(output_file)}")
    return True


# =============================================================================
# MAIN
# =============================================================================

def main():
    args = sys.argv[1:]
    build_pdf = '--pdf' in args or '--all' in args
    build_epub_flag = '--epub' in args or '--all' in args

    print(f"Found {len(CHAPTER_FILES)} chapter files")
    print(f"Book: {BOOK_TITLE} (Book {BOOK_NUMBER} of {SERIES_NAME})")
    print(f"Paperback size: {PAPERBACK_SIZE}")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Build chapter content (shared)
    chapter_parts = build_chapters_and_back()

    # DOCX version (HTML title page + manual TOC)
    docx_parts = [build_docx_front_matter(CHAPTER_FILES)] + chapter_parts
    docx_manuscript = '\n'.join(docx_parts)
    with open(OUTPUT_DOCX, 'w') as f:
        f.write(docx_manuscript)
    print(f"\nDOCX source: {os.path.basename(OUTPUT_DOCX)} ({len(docx_manuscript.split()):,} words)")

    # PDF version (no HTML title — handled by title.tex)
    pdf_parts = [build_pdf_front_matter(CHAPTER_FILES)] + chapter_parts
    pdf_manuscript = '\n'.join(pdf_parts)
    with open(OUTPUT_PDF, 'w') as f:
        f.write(pdf_manuscript)
    print(f"PDF source:  {os.path.basename(OUTPUT_PDF)} ({len(pdf_manuscript.split()):,} words)")

    # Build outputs
    if build_pdf:
        build_paperback_pdf()

    if build_epub_flag:
        build_epub()

    if not build_pdf and not build_epub_flag:
        print(f"\nTo build outputs, run:")
        print(f"  python3 {os.path.basename(__file__)} --pdf    # paperback PDF")
        print(f"  python3 {os.path.basename(__file__)} --epub   # ebook EPUB")
        print(f"  python3 {os.path.basename(__file__)} --all    # everything")


if __name__ == '__main__':
    main()
