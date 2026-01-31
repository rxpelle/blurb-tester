#!/usr/bin/env python3
"""
Baseline Generator for Plague Novel Series
Generates BOOK_BASELINE.md files from actual manuscript chapters.

Usage:
    python generate_baseline.py book_1_aethelred_cipher
    python generate_baseline.py --all  # Generate for all books
"""

import os
import re
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib


class BaselineGenerator:
    """Generates canonical baseline documentation from manuscript chapters."""

    # Keywords to extract from text
    SEVEN_KEYS = ['Pattern Eye', 'Time Key', 'Blood Cipher', 'Memory Matrix',
                  'Network Seed', 'Synthesis Protocol', 'Final Key']

    NETWORK_KEYWORDS = ['Network', 'Brotherhood', 'Order', 'Society', 'Circle']

    def __init__(self, book_dir: Path):
        self.book_dir = Path(book_dir)
        self.book_name = book_dir.name
        self.chapters_dir = book_dir / 'manuscript' / 'chapters'
        self.metadata_cache = {}

    def extract_metadata_from_chapter(self, chapter_file: Path) -> Dict:
        """Extract YAML frontmatter metadata if present."""
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1])
                    return metadata if metadata else {}
                except yaml.YAMLError:
                    pass

        return {}

    def extract_chapter_summary(self, chapter_file: Path, max_lines: int = 50) -> Dict:
        """Extract key information from a chapter file."""
        with open(chapter_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove YAML frontmatter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]

        # Extract title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled"

        # Extract chapter number
        chapter_num_match = re.search(r'chapter[_\s](\d+)', chapter_file.stem, re.IGNORECASE)
        chapter_num = int(chapter_num_match.group(1)) if chapter_num_match else 0

        # Word count
        words = len(content.split())

        # Extract dates mentioned (BCE/CE years)
        dates = re.findall(r'\b(\d{1,4})\s*(BCE|CE|AD)\b', content, re.IGNORECASE)
        dates = list(set([f"{d[0]} {d[1].upper()}" for d in dates]))

        # Extract character names (capitalized words, potential names)
        # Look for patterns like "Brother Marcus" or single capitalized names in dialogue
        potential_characters = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', content)
        # Filter out common words and keep likely names (appears multiple times)
        char_counts = {}
        for char in potential_characters:
            if len(char) > 2 and char not in ['The', 'Chapter', 'Book', 'He', 'She', 'They']:
                char_counts[char] = char_counts.get(char, 0) + 1

        # Characters mentioned 3+ times are likely important
        characters = [char for char, count in char_counts.items() if count >= 3][:10]

        # Seven Keys mentions
        keys_mentioned = []
        for key in self.SEVEN_KEYS:
            if key in content:
                keys_mentioned.append(key)

        # Network mentions
        network_terms = []
        for term in self.NETWORK_KEYWORDS:
            if term in content:
                network_terms.append(term)

        # Extract key scenes (paragraphs with action/revelation keywords)
        action_keywords = ['discovered', 'revealed', 'realized', 'found', 'died',
                          'attacked', 'escaped', 'learned', 'understood']

        sentences = re.split(r'[.!?]+', content)
        key_moments = []
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in action_keywords):
                if len(sentence) > 20 and len(sentence) < 200:
                    key_moments.append(sentence)
                    if len(key_moments) >= 5:
                        break

        return {
            'chapter_num': chapter_num,
            'title': title,
            'file': chapter_file.name,
            'word_count': words,
            'dates_mentioned': sorted(dates),
            'characters': sorted(characters)[:10],
            'seven_keys_mentioned': keys_mentioned,
            'network_terms': network_terms,
            'key_moments': key_moments[:5],
            'modified_date': datetime.fromtimestamp(chapter_file.stat().st_mtime).isoformat()
        }

    def generate_checksum(self, chapters: List[Path]) -> str:
        """Generate SHA256 checksum of all chapter contents for verification."""
        hasher = hashlib.sha256()
        for chapter in sorted(chapters):
            with open(chapter, 'rb') as f:
                hasher.update(f.read())
        return hasher.hexdigest()[:16]

    def extract_book_metadata(self) -> Dict:
        """Extract or infer metadata about the entire book."""
        book_config = self.book_dir / '.baseline_config.json'

        if book_config.exists():
            with open(book_config, 'r') as f:
                return json.load(f)

        # Infer from directory name
        parts = self.book_name.split('_')
        book_num = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        book_title = ' '.join(parts[2:]).replace('_', ' ').title() if len(parts) > 2 else "Unknown"

        return {
            'book_number': book_num,
            'book_title': book_title,
            'status': 'unknown',
            'time_period': 'unknown',
            'pov_character': 'unknown'
        }

    def generate_baseline(self) -> str:
        """Generate complete BOOK_BASELINE.md content."""
        if not self.chapters_dir.exists():
            return f"# ERROR: No chapters directory found at {self.chapters_dir}"

        # Get all chapter files
        chapter_files = sorted(self.chapters_dir.glob('*.md'))
        if not chapter_files:
            return f"# ERROR: No chapter files found in {self.chapters_dir}"

        # Extract metadata from each chapter
        chapters_data = []
        for chapter_file in chapter_files:
            chapter_info = self.extract_chapter_summary(chapter_file)
            chapter_metadata = self.extract_metadata_from_chapter(chapter_file)
            chapter_info['metadata'] = chapter_metadata
            chapters_data.append(chapter_info)

        # Sort by chapter number
        chapters_data.sort(key=lambda x: x['chapter_num'])

        # Book-level metadata
        book_meta = self.extract_book_metadata()

        # Calculate totals
        total_words = sum(ch['word_count'] for ch in chapters_data)
        all_dates = []
        for ch in chapters_data:
            all_dates.extend(ch['dates_mentioned'])
        unique_dates = sorted(set(all_dates))

        all_characters = []
        for ch in chapters_data:
            all_characters.extend(ch['characters'])
        # Count character frequency across all chapters
        char_freq = {}
        for char in all_characters:
            char_freq[char] = char_freq.get(char, 0) + 1
        major_characters = sorted(char_freq.items(), key=lambda x: x[1], reverse=True)[:15]

        all_keys = []
        for ch in chapters_data:
            all_keys.extend(ch['seven_keys_mentioned'])
        keys_in_book = sorted(set(all_keys))

        # Generate checksum
        checksum = self.generate_checksum(chapter_files)

        # Build baseline document
        baseline = f"""# {book_meta.get('book_title', 'Unknown Book')} - CANONICAL BASELINE

**Book Number**: {book_meta.get('book_number', 'Unknown')}
**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Source**: Auto-generated from {len(chapters_data)} manuscript chapters
**Total Word Count**: {total_words:,} words
**Verification Checksum**: `{checksum}`

---

## ⚠️ IMPORTANT - SOURCE OF TRUTH

This baseline was **automatically generated from the actual manuscript chapters**.

**DO NOT TRUST**:
- Old outline files
- Summary documents created before this baseline
- Memory of previous sessions

**ALWAYS VERIFY**:
1. Check this BOOK_BASELINE.md first
2. If uncertain, read the actual chapter files
3. Update this baseline after any chapter modifications

---

## Quick Reference

- **Time Period**: {book_meta.get('time_period', 'See dates below')}
- **POV Character**: {book_meta.get('pov_character', 'See characters below')}
- **Status**: {book_meta.get('status', 'Unknown')}
- **Date Range**: {unique_dates[0] if unique_dates else 'Unknown'} to {unique_dates[-1] if len(unique_dates) > 1 else 'Unknown'}

### Seven Keys Status in This Book
"""

        if keys_in_book:
            for key in keys_in_book:
                baseline += f"- **{key}**: Mentioned in this book\n"
        else:
            baseline += "- No Seven Keys explicitly mentioned in extracted text\n"

        baseline += f"""
### Major Characters (by appearance frequency)
"""
        for char, count in major_characters[:10]:
            baseline += f"- **{char}**: {count} mentions across chapters\n"

        baseline += f"""
---

## Chapter-by-Chapter Summary (FROM ACTUAL TEXT)

"""

        for chapter in chapters_data:
            baseline += f"""### Chapter {chapter['chapter_num']}: {chapter['title']}

**File**: `{chapter['file']}`
**Word Count**: {chapter['word_count']:,}
**Last Modified**: {chapter['modified_date']}

"""

            # Add metadata if present
            if chapter['metadata']:
                baseline += "**Metadata**:\n"
                for key, value in chapter['metadata'].items():
                    baseline += f"- {key}: {value}\n"
                baseline += "\n"

            if chapter['dates_mentioned']:
                baseline += f"**Dates**: {', '.join(chapter['dates_mentioned'])}\n\n"

            if chapter['characters']:
                baseline += f"**Characters**: {', '.join(chapter['characters'][:8])}\n\n"

            if chapter['seven_keys_mentioned']:
                baseline += f"**Seven Keys**: {', '.join(chapter['seven_keys_mentioned'])}\n\n"

            if chapter['key_moments']:
                baseline += "**Key Moments**:\n"
                for moment in chapter['key_moments']:
                    baseline += f"- {moment.strip()}\n"
                baseline += "\n"

            baseline += "---\n\n"

        baseline += f"""
## Continuity Anchors

### Timeline Events Mentioned
"""
        for date in unique_dates[:20]:  # Top 20 dates
            baseline += f"- {date}\n"

        baseline += f"""
### Seven Keys Tracking
"""
        if keys_in_book:
            for key in keys_in_book:
                # Find which chapters mention this key
                chapters_with_key = [ch['chapter_num'] for ch in chapters_data if key in ch['seven_keys_mentioned']]
                baseline += f"- **{key}**: Chapters {', '.join(map(str, chapters_with_key))}\n"
        else:
            baseline += "- No Seven Keys explicitly tracked in this book\n"

        baseline += f"""
---

## Verification & Update Protocol

**Checksum**: `{checksum}`

This checksum is generated from all chapter files. If chapters are modified:
1. Re-run baseline generator: `python generate_baseline.py {self.book_name}`
2. Update CANONICAL_SERIES_INDEX.md
3. Commit changes with note about which chapters changed

**Last Generation**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Source Files**: {len(chapters_data)} chapters in `manuscript/chapters/`

---

**Note**: This is a living document. Regenerate after any manuscript changes.
"""

        return baseline


def generate_for_book(book_dir: str) -> None:
    """Generate baseline for a specific book."""
    book_path = Path(book_dir)
    if not book_path.exists():
        print(f"ERROR: Book directory not found: {book_dir}")
        return

    print(f"Generating baseline for {book_path.name}...")

    generator = BaselineGenerator(book_path)
    baseline_content = generator.generate_baseline()

    # Write to BOOK_BASELINE.md
    output_file = book_path / 'BOOK_BASELINE.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(baseline_content)

    print(f"✓ Generated: {output_file}")
    print(f"  Word count: {baseline_content.count(' ')}")
    print()


def generate_all_baselines() -> None:
    """Generate baselines for all book directories."""
    current_dir = Path('.')
    book_dirs = sorted([d for d in current_dir.iterdir() if d.is_dir() and d.name.startswith('book_')])

    print(f"Found {len(book_dirs)} book directories")
    print()

    for book_dir in book_dirs:
        try:
            generate_for_book(str(book_dir))
        except Exception as e:
            print(f"ERROR generating baseline for {book_dir.name}: {e}")
            print()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == '--all':
            generate_all_baselines()
        else:
            generate_for_book(sys.argv[1])
    else:
        print("Usage:")
        print("  python generate_baseline.py book_1_aethelred_cipher")
        print("  python generate_baseline.py --all")
