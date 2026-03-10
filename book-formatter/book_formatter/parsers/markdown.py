"""Parse markdown manuscript files into the internal Book model."""

import glob
import os
import re

from book_formatter.config import BookConfig
from book_formatter.parsers.ast_model import Book, Chapter


def parse_manuscript(config: BookConfig) -> Book:
    """Parse a manuscript directory or single file into a Book model."""
    manuscript_path = config.resolve_path(config.manuscript)

    if os.path.isfile(manuscript_path):
        return _parse_single_file(manuscript_path)
    elif os.path.isdir(manuscript_path):
        return _parse_directory(manuscript_path, config.chapter_pattern)
    else:
        raise FileNotFoundError(
            f"Manuscript not found: {manuscript_path}\n"
            f"Set 'manuscript' in book.yaml to a directory or file path."
        )


def _parse_directory(directory: str, pattern: str) -> Book:
    """Parse a directory of numbered markdown chapter files."""
    chapter_files = sorted(glob.glob(os.path.join(directory, pattern)))

    if not chapter_files:
        raise FileNotFoundError(
            f"No chapter files matching '{pattern}' found in {directory}"
        )

    chapters = []
    for i, filepath in enumerate(chapter_files):
        chapter = _parse_chapter_file(filepath, i + 1)
        chapters.append(chapter)

    book = Book(chapters=chapters)
    book.calculate_stats()
    return book


def _parse_single_file(filepath: str) -> Book:
    """Parse a single markdown file, splitting on # headings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split on level-1 headings
    parts = re.split(r'^(# .+)$', content, flags=re.MULTILINE)

    chapters = []
    chapter_num = 0

    i = 1  # Skip content before first heading
    while i < len(parts):
        heading = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ''
        chapter_num += 1

        title = heading.lstrip('# ').strip()
        # Remove any {#anchor} attributes
        title = re.sub(r'\s*\{#[^}]+\}', '', title)

        full_content = heading + '\n' + body

        chapter = Chapter(
            number=chapter_num,
            title=title,
            content=full_content.strip(),
            source_file=filepath,
            word_count=len(body.split()),
        )
        _detect_special_chapter(chapter)
        chapters.append(chapter)
        i += 2

    book = Book(chapters=chapters)
    book.calculate_stats()
    return book


def _parse_chapter_file(filepath: str, default_number: int) -> Chapter:
    """Parse a single chapter markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    basename = os.path.basename(filepath).replace('.md', '')

    # Extract number and title from filename (e.g., "01_THE_BURNING.md")
    match = re.match(r'^(\d+)_(.+)$', basename)
    if match:
        number = int(match.group(1))
        title = match.group(2).replace('_', ' ').title()
        # Fix common title-case issues
        for word in ('And', 'The', 'Of', 'In', 'A', 'An', 'Or', 'But', 'For', 'Nor', 'On', 'At', 'To', 'By'):
            title = title.replace(f' {word} ', f' {word.lower()} ')
    else:
        number = default_number
        title = basename.replace('_', ' ').title()

    # Clean up content
    # Remove END CHAPTER markers
    content = re.sub(
        r'\n+\*?\*?---\*?\*?\s*\n+\*?\*?END CHAPTER \d+\*?\*?\s*$',
        '', content, flags=re.MULTILINE
    )

    word_count = len(content.split())

    chapter = Chapter(
        number=number,
        title=title,
        content=content.strip(),
        source_file=filepath,
        word_count=word_count,
    )
    _detect_special_chapter(chapter)
    return chapter


def _detect_special_chapter(chapter: Chapter):
    """Detect epilogues, prologues, previews from title/content."""
    title_lower = chapter.title.lower()
    if 'epilogue' in title_lower:
        chapter.is_epilogue = True
        chapter.is_unnumbered = True
    elif 'prologue' in title_lower:
        chapter.is_unnumbered = True
    elif 'preview' in title_lower:
        chapter.is_preview = True
        chapter.is_unnumbered = True
