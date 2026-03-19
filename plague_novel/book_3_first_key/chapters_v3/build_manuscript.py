#!/usr/bin/env python3
"""Build combined manuscript for The First Key (Book 3)."""

import os
import re
import glob

CHAPTERS_V2 = os.path.join(os.path.dirname(__file__), '..', 'chapters_v2')
OUTPUT_DOCX = os.path.join(os.path.dirname(__file__), 'The First Key - Complete with Front Matter.md')
OUTPUT_PDF = os.path.join(os.path.dirname(__file__), 'The First Key - PDF Source.md')

# Chapter titles for TOC (extracted from filenames)
CHAPTER_FILES = sorted(glob.glob(os.path.join(CHAPTERS_V2, '[0-1][0-9]_*.md')))


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
    return int(num), title


def make_anchor(num, title):
    """Create anchor ID like #chapter-1"""
    if num == 13:
        return 'epilogue'
    if num == 14:
        return 'book4-preview'
    return f'chapter-{num}'


def build_about_and_toc(chapters):
    """Build about author and TOC sections (shared by both outputs)."""
    lines = []

    # About the Author
    lines.append('# About the Author {.unnumbered}\n')
    lines.append('Randy Pellegrini writes *The Architecture of Survival*, a 12-book epic spanning 3,200 years from Bronze Age Egypt to the modern era. The series explores genetic memory as hard science, civilizational collapse patterns, and the moral complexity of two competing philosophies: knowledge preservation versus genetic control.\n')
    lines.append('The saga weaves real historical events with speculative elements grounded in epigenetics, network theory, and systems thinking. Each book stands alone while revealing how defensive methodology has been embedded into human civilization through every era\'s dominant technology.\n')
    lines.append('When not writing, Randy travels near and far to better imagine history up close and personal. He continuously wonders why we continue to replay broken patterns of human systems. That wonder was the seed that has grown into this series.\n')
    lines.append('To learn more about the book series, visit [randypellegrini.com/series](https://randypellegrini.com/series)\n')
    lines.append('\n\\newpage\n')

    return '\n'.join(lines)


def build_docx_front_matter(chapters):
    """Build HTML title page + about author + TOC for DOCX output."""
    lines = []

    # HTML title page (renders well in DOCX)
    lines.append('\\newpage\n')
    lines.append('<p style="text-align: center; margin-top: 4cm;">')
    lines.append('<span style="font-size: 2.5em; font-weight: bold;">THE FIRST KEY</span>')
    lines.append('</p>\n')
    lines.append('<p style="text-align: center; margin-top: 0.5cm;">')
    lines.append('<span style="font-size: 1.2em;">Book 3 of The Architecture of Survival</span>')
    lines.append('</p>\n')
    lines.append('<p style="text-align: center; margin-top: 2cm;">')
    lines.append('<span style="font-size: 1.5em;">Randy Pellegrini</span>')
    lines.append('</p>\n')
    lines.append('<p style="text-align: center; margin-top: 3cm;">')
    lines.append('</p>\n')
    lines.append('[randypellegrini.com](https://randypellegrini.com)\n')
    lines.append('Copyright \u00a9 2026 Randy Pellegrini\n')
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
        if num == 13:
            lines.append(f'[**EPILOGUE** - The Physician\'s Rest](#{anchor})\n')
        elif num == 14:
            lines.append(f'[**PREVIEW: BOOK 4** - The Prophet\'s Burden](#{anchor})\n')
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


def process_chapter(filepath):
    """Read a chapter file and clean it for the combined manuscript."""
    with open(filepath, 'r') as f:
        content = f.read()

    num, title = clean_title(filepath)
    anchor = make_anchor(num, title)

    # Remove END CHAPTER markers
    content = re.sub(r'\n+\*?\*?---\*?\*?\s*\n+\*?\*?END CHAPTER \d+\*?\*?\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n+---\s*\n+\*?\*?END CHAPTER \d+\*?\*?\s*$', '', content, flags=re.MULTILINE)

    # Replace the original header with properly formatted one
    if num == 13:
        # Epilogue
        content = re.sub(r'^# EPILOGUE:?\s*.*$', f'# EPILOGUE - THE PHYSICIAN\'S REST {{#{anchor}}}', content, count=1, flags=re.MULTILINE)
    elif num == 14:
        # Book 4 Preview
        content = re.sub(r'^# PREVIEW:?\s*.*$', f'# PREVIEW: BOOK 4 - THE PROPHET\'S BURDEN {{#{anchor}}}', content, count=1, flags=re.MULTILINE)
    else:
        # Regular chapter - replace header line
        content = re.sub(
            r'^# CHAPTER \d+\s*-\s*.*$',
            f'# CHAPTER {num} - {title.upper()} {{#{anchor}}}',
            content, count=1, flags=re.MULTILINE
        )

    return content.rstrip() + '\n'


def build_back_matter():
    """Build the end-of-book section."""
    lines = []
    lines.append('\n\\newpage\n')
    lines.append('* * *\n')
    lines.append('**Continue reading in Book 4: THE PROPHET\'S BURDEN**\n')
    lines.append('One thousand years after Nefertari created the Genesis Protocol, a carpenter\'s son in Galilee carries Generation 41 of the bloodline \u2014 and his teachings will reshape the network\'s mission for two millennia.\n')
    lines.append('For more information on the books in this series and to better understand the meaning behind the concepts these books elicit, go to the author\'s webpage [randypellegrini.com/series](https://randypellegrini.com/series).\n')
    lines.append('Looking forward to your feedback and correspondence,\n')
    lines.append('Randy Pellegrini\n')
    lines.append('\n\\newpage\n')
    return '\n'.join(lines)


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


def main():
    print(f"Found {len(CHAPTER_FILES)} chapter files")

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


if __name__ == '__main__':
    main()
