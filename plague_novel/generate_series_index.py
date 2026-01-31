#!/usr/bin/env python3
"""
Generate CANONICAL_SERIES_INDEX.md from all BOOK_BASELINE.md files.

This creates the master series-level index that syncs from individual book baselines.

Usage:
    python generate_series_index.py
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class SeriesIndexGenerator:
    """Generates the canonical series index from book baselines."""

    def __init__(self, root_dir: Path = Path('.')):
        self.root_dir = root_dir
        self.books_data = []

    def parse_baseline_file(self, baseline_path: Path) -> Dict:
        """Extract key information from a BOOK_BASELINE.md file."""

        if not baseline_path.exists():
            return None

        with open(baseline_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata from the file
        data = {
            'book_dir': baseline_path.parent.name,
            'baseline_path': str(baseline_path),
        }

        # Extract book number
        match = re.search(r'\*\*Book Number\*\*:\s*(\d+)', content)
        data['book_number'] = int(match.group(1)) if match else 0

        # Extract title
        title_match = re.search(r'^#\s+(.+?)\s*-\s*CANONICAL BASELINE', content, re.MULTILINE)
        data['title'] = title_match.group(1).strip() if title_match else "Unknown"

        # Extract last updated
        match = re.search(r'\*\*Last Updated\*\*:\s*(.+)$', content, re.MULTILINE)
        data['last_updated'] = match.group(1).strip() if match else "Unknown"

        # Extract word count
        match = re.search(r'\*\*Total Word Count\*\*:\s*([\d,]+)\s*words', content)
        if match:
            data['word_count'] = int(match.group(1).replace(',', ''))
        else:
            data['word_count'] = 0

        # Extract checksum
        match = re.search(r'\*\*Verification Checksum\*\*:\s*`([^`]+)`', content)
        data['checksum'] = match.group(1) if match else "unknown"

        # Extract time period
        match = re.search(r'\*\*Time Period\*\*:\s*(.+)$', content, re.MULTILINE)
        data['time_period'] = match.group(1).strip() if match else "unknown"

        # Extract POV character
        match = re.search(r'\*\*POV Character\*\*:\s*(.+)$', content, re.MULTILINE)
        data['pov_character'] = match.group(1).strip() if match else "unknown"

        # Extract status
        match = re.search(r'\*\*Status\*\*:\s*(.+)$', content, re.MULTILINE)
        data['status'] = match.group(1).strip() if match else "unknown"

        # Extract Seven Keys mentions
        seven_keys_section = re.search(
            r'### Seven Keys Status in This Book(.+?)(?=###|---|\Z)',
            content,
            re.DOTALL
        )
        if seven_keys_section:
            keys = re.findall(r'-\s*\*\*([^*]+)\*\*:', seven_keys_section.group(1))
            data['seven_keys'] = keys
        else:
            data['seven_keys'] = []

        # Extract major characters
        char_section = re.search(
            r'### Major Characters \(by appearance frequency\)(.+?)(?=###|---|\Z)',
            content,
            re.DOTALL
        )
        if char_section:
            chars = re.findall(r'-\s*\*\*([^*]+)\*\*:', char_section.group(1))
            data['major_characters'] = chars[:5]  # Top 5
        else:
            data['major_characters'] = []

        # Count chapters
        chapter_matches = re.findall(r'^### Chapter \d+:', content, re.MULTILINE)
        data['chapter_count'] = len(chapter_matches)

        return data

    def find_all_baselines(self) -> List[Dict]:
        """Find all BOOK_BASELINE.md files in book directories."""

        book_dirs = sorted([d for d in self.root_dir.iterdir()
                           if d.is_dir() and d.name.startswith('book_')])

        baselines = []
        for book_dir in book_dirs:
            baseline_path = book_dir / 'BOOK_BASELINE.md'
            if baseline_path.exists():
                data = self.parse_baseline_file(baseline_path)
                if data:
                    baselines.append(data)
            else:
                # Book exists but no baseline yet
                baselines.append({
                    'book_dir': book_dir.name,
                    'book_number': self._extract_book_number(book_dir.name),
                    'title': 'No Baseline Generated',
                    'status': 'missing_baseline',
                    'baseline_path': None
                })

        # Sort by book number
        baselines.sort(key=lambda x: x.get('book_number', 999))

        return baselines

    def _extract_book_number(self, dirname: str) -> int:
        """Extract book number from directory name."""
        match = re.search(r'book[_\s](\d+)', dirname, re.IGNORECASE)
        return int(match.group(1)) if match else 999

    def generate_index(self) -> str:
        """Generate the complete CANONICAL_SERIES_INDEX.md content."""

        baselines = self.find_all_baselines()

        # Statistics
        total_books = len(baselines)
        completed_books = len([b for b in baselines if b.get('word_count', 0) > 0])
        total_words = sum(b.get('word_count', 0) for b in baselines)

        # Build index content
        index = f"""# Plague Novel Series - CANONICAL SERIES INDEX

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Auto-Synced From**: Individual BOOK_BASELINE.md files
**Total Books**: {total_books}
**Completed Books with Baselines**: {completed_books}
**Total Word Count**: {total_words:,} words

---

## ⚠️ SOURCE OF TRUTH HIERARCHY

When working on this series, **ALWAYS follow this verification order**:

### 1. Individual Book Baselines (HIGHEST AUTHORITY)
Check the specific book's `BOOK_BASELINE.md` file first:
- Contains actual chapter summaries extracted from manuscript
- Includes verification checksums
- Updated automatically when chapters change

### 2. This Series Index (SERIES-LEVEL OVERVIEW)
Use this file for:
- Cross-book continuity (Seven Keys custody chain, timeline events)
- Understanding the big picture
- Finding which book contains what information

### 3. Actual Chapter Files (ULTIMATE SOURCE)
If baseline seems wrong or outdated:
- Read the actual chapter markdown files
- They are the ultimate source of truth
- Then regenerate the baseline

### ❌ DO NOT TRUST
- Old outline files (unless explicitly marked as "synced with baseline")
- SERIES_BIBLE files older than baseline generation dates
- Summary documents without verification checksums
- Your memory from previous sessions
- Any document that contradicts a BOOK_BASELINE.md file

---

## Book Status Overview

"""

        # Build book status table
        index += "| Book | Title | Status | Words | POV | Time Period | Last Updated |\n"
        index += "|------|-------|--------|-------|-----|-------------|-------------|\n"

        for book in baselines:
            book_num = book.get('book_number', '?')
            title = book.get('title', 'Unknown')
            status_icon = self._get_status_icon(book)
            word_count = f"{book.get('word_count', 0):,}" if book.get('word_count') else '-'
            pov = book.get('pov_character', '-')
            time_period = book.get('time_period', '-')
            last_updated = book.get('last_updated', '-')

            # Truncate long fields for table
            if len(pov) > 20:
                pov = pov[:17] + '...'
            if len(time_period) > 25:
                time_period = time_period[:22] + '...'

            index += f"| {book_num} | {title} | {status_icon} | {word_count} | {pov} | {time_period} | {last_updated} |\n"

        index += "\n**Status Legend**:\n"
        index += "- ✅ Complete with baseline\n"
        index += "- ⚠️ Needs baseline generation\n"
        index += "- 📝 In progress\n\n"

        index += "---\n\n"

        # Seven Keys tracking across series
        index += "## Seven Keys Custody Chain (FROM BASELINES)\n\n"
        index += "Track the Seven Keys as they appear and transfer across books:\n\n"

        all_keys = ['Pattern Eye', 'Time Key', 'Blood Cipher', 'Memory Matrix',
                   'Network Seed', 'Synthesis Protocol', 'Final Key']

        for key in all_keys:
            index += f"### {key}\n\n"
            books_with_key = [(b['book_number'], b['title']) for b in baselines
                             if key in b.get('seven_keys', [])]

            if books_with_key:
                for book_num, book_title in books_with_key:
                    index += f"- **Book {book_num} ({book_title})**: Mentioned in baseline\n"
            else:
                index += "- No baseline mentions yet (check individual chapters or add to baseline)\n"

            index += "\n"

        # Character tracking
        index += "---\n\n## Major Characters Across Series\n\n"
        index += "Characters that appear prominently in each book (from baselines):\n\n"

        for book in baselines:
            if book.get('major_characters'):
                book_num = book.get('book_number', '?')
                title = book.get('title', 'Unknown')
                index += f"### Book {book_num}: {title}\n"
                for char in book['major_characters']:
                    index += f"- {char}\n"
                index += "\n"

        # Timeline
        index += "---\n\n## Series Timeline (FROM BASELINES)\n\n"

        for book in baselines:
            if book.get('time_period') and book.get('time_period') != 'unknown':
                book_num = book.get('book_number', '?')
                title = book.get('title', 'Unknown')
                time_period = book.get('time_period')
                index += f"- **Book {book_num}** ({title}): {time_period}\n"

        # Update protocol
        index += f"""
---

## Baseline Update Protocol

### When to Regenerate Baselines

Regenerate a book's baseline whenever:
1. You modify any chapter file
2. You add new chapters
3. You fix continuity issues
4. A baseline is more than 7 days old during active editing

### How to Regenerate

```bash
# Single book
python generate_baseline.py book_1_aethelred_cipher

# All books
python generate_baseline.py --all

# Then update this series index
python generate_series_index.py
```

### Verification

Each baseline includes a checksum. If you're unsure if a baseline is current:
1. Check the checksum in BOOK_BASELINE.md
2. Regenerate and compare checksums
3. If different, baseline was out of date

---

## Session Start Protocol

**At the beginning of EVERY new session:**

1. Read `CANONICAL_SERIES_INDEX.md` (this file)
2. If working on a specific book, read that book's `BOOK_BASELINE.md`
3. Note the "Last Updated" dates
4. If baselines are stale (>7 days during active work), regenerate
5. NEVER trust outline files without checking baselines first

**Before making any changes:**

1. Read the relevant `BOOK_BASELINE.md`
2. If uncertain, read the actual chapter files
3. Make your changes
4. Regenerate the baseline: `python generate_baseline.py book_X_name`
5. Update this index: `python generate_series_index.py`

---

## Book Details

"""

        # Detailed book information
        for book in baselines:
            if book.get('baseline_path'):
                book_num = book.get('book_number', '?')
                title = book.get('title', 'Unknown')
                index += f"### Book {book_num}: {title}\n\n"
                index += f"**Directory**: `{book['book_dir']}`\n"
                index += f"**Baseline**: `{book['baseline_path']}`\n"
                index += f"**Word Count**: {book.get('word_count', 0):,}\n"
                index += f"**Chapters**: {book.get('chapter_count', 0)}\n"
                index += f"**POV Character**: {book.get('pov_character', 'unknown')}\n"
                index += f"**Time Period**: {book.get('time_period', 'unknown')}\n"
                index += f"**Checksum**: `{book.get('checksum', 'unknown')}`\n"
                index += f"**Last Updated**: {book.get('last_updated', 'unknown')}\n"

                if book.get('seven_keys'):
                    index += f"**Seven Keys**: {', '.join(book['seven_keys'])}\n"

                index += "\n"

        index += f"""
---

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Baselines Found**: {len([b for b in baselines if b.get('baseline_path')])}
**Total Books**: {total_books}
"""

        return index

    def _get_status_icon(self, book: Dict) -> str:
        """Get status icon for a book."""
        if not book.get('baseline_path'):
            return "⚠️ No baseline"
        elif book.get('word_count', 0) > 50000:
            return "✅ Complete"
        elif book.get('word_count', 0) > 0:
            return "📝 In progress"
        else:
            return "⚠️ Check"


def main():
    """Generate the series index."""
    print("Generating CANONICAL_SERIES_INDEX.md...")

    generator = SeriesIndexGenerator()
    index_content = generator.generate_index()

    output_path = Path('CANONICAL_SERIES_INDEX.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(index_content)

    print(f"✓ Generated: {output_path}")
    print(f"  Size: {len(index_content):,} characters")
    print()


if __name__ == '__main__':
    main()
