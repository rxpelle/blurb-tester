#!/usr/bin/env python3
"""
Add YAML frontmatter metadata headers to chapter files.

Usage:
    python add_metadata_header.py book_1_aethelred_cipher/manuscript/chapters/chapter_1_medieval_REVISED.md \
        --chapter 1 \
        --title "The Key" \
        --date "1347 CE" \
        --pov "Thomas" \
        --key-events "Discovery of grandfather's cipher" "Meeting with Margarethe"
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List


def read_file_content(file_path: Path) -> str:
    """Read file content, return text without existing frontmatter."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # If frontmatter exists, remove it
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[2].lstrip()  # Return content without frontmatter

    return content


def create_metadata_header(
    book: int,
    chapter: int,
    title: str,
    date_written: str = None,
    pov_character: str = None,
    key_events: List[str] = None,
    continuity_tags: List[str] = None,
    seven_keys: List[str] = None,
    characters_introduced: List[str] = None,
    **kwargs
) -> str:
    """Create YAML frontmatter metadata."""

    metadata = {
        'book': book,
        'chapter': chapter,
        'title': title,
    }

    if date_written:
        metadata['date_written'] = date_written

    if pov_character:
        metadata['pov_character'] = pov_character

    if key_events:
        metadata['key_events'] = key_events

    if seven_keys:
        metadata['seven_keys'] = seven_keys

    if characters_introduced:
        metadata['characters_introduced'] = characters_introduced

    if continuity_tags:
        metadata['continuity_tags'] = continuity_tags

    # Add any additional kwargs
    for key, value in kwargs.items():
        if value:
            metadata[key] = value

    # Convert to YAML
    yaml_str = yaml.dump(metadata, default_flow_style=False, sort_keys=False)

    return f"---\n{yaml_str}---\n\n"


def add_metadata_to_file(
    file_path: Path,
    metadata: Dict,
    dry_run: bool = False
) -> None:
    """Add metadata header to a chapter file."""

    content = read_file_content(file_path)

    # Create metadata header
    header = create_metadata_header(**metadata)

    # Combine
    new_content = header + content

    if dry_run:
        print(f"\nPreview for {file_path.name}:")
        print("=" * 60)
        print(new_content[:500])
        print("=" * 60)
    else:
        # Backup original
        backup_path = file_path.with_suffix('.md.backup')
        if not backup_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                with open(backup_path, 'w', encoding='utf-8') as b:
                    b.write(f.read())

        # Write new content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✓ Added metadata to {file_path.name}")
        print(f"  Backup saved: {backup_path.name}")


def batch_add_metadata(book_dir: Path, metadata_config: Dict) -> None:
    """Add metadata to all chapters based on config file."""

    chapters_dir = book_dir / 'manuscript' / 'chapters'
    if not chapters_dir.exists():
        print(f"ERROR: No chapters directory found at {chapters_dir}")
        return

    chapter_files = sorted(chapters_dir.glob('chapter_*.md'))

    for chapter_file in chapter_files:
        # Try to extract chapter number from filename
        import re
        match = re.search(r'chapter[_\s](\d+)', chapter_file.stem, re.IGNORECASE)
        if not match:
            continue

        chapter_num = int(match.group(1))

        # Look for this chapter in config
        chapter_key = f"chapter_{chapter_num}"
        if chapter_key in metadata_config:
            metadata = metadata_config[chapter_key]
            metadata['book'] = metadata_config.get('book_number', 1)
            metadata['chapter'] = chapter_num

            add_metadata_to_file(chapter_file, metadata, dry_run=False)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    # Simple single-file mode
    if sys.argv[1].endswith('.md'):
        file_path = Path(sys.argv[1])

        # Parse arguments
        metadata = {
            'book': 1,
            'chapter': 1,
            'title': 'Untitled'
        }

        i = 2
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--chapter' and i + 1 < len(sys.argv):
                metadata['chapter'] = int(sys.argv[i + 1])
                i += 2
            elif arg == '--title' and i + 1 < len(sys.argv):
                metadata['title'] = sys.argv[i + 1]
                i += 2
            elif arg == '--date' and i + 1 < len(sys.argv):
                metadata['date_written'] = sys.argv[i + 1]
                i += 2
            elif arg == '--pov' and i + 1 < len(sys.argv):
                metadata['pov_character'] = sys.argv[i + 1]
                i += 2
            elif arg == '--key-events':
                events = []
                i += 1
                while i < len(sys.argv) and not sys.argv[i].startswith('--'):
                    events.append(sys.argv[i])
                    i += 1
                metadata['key_events'] = events
            else:
                i += 1

        add_metadata_to_file(file_path, metadata, dry_run='--dry-run' in sys.argv)

    else:
        print("Batch mode not implemented in this version")
        print("Use: python add_metadata_header.py <chapter_file.md> --chapter 1 --title 'Title'")
