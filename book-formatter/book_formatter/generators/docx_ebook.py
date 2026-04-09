"""DOCX ebook generator using Pandoc — for KDP and other platforms that accept .docx."""

import os
import re

from book_formatter.config import BookConfig
from book_formatter.parsers.ast_model import Book
from book_formatter.generators.base import BaseGenerator


class DOCXEbookGenerator(BaseGenerator):
    """Generate a DOCX ebook for KDP upload."""

    format_name = 'docx'
    file_extension = 'docx'

    def _heading_to_anchor(self, title: str) -> str:
        """Convert a heading title to Pandoc's auto-generated anchor ID."""
        anchor = title.lower()
        anchor = re.sub(r"[^\w\s-]", '', anchor)
        anchor = re.sub(r'\s+', '-', anchor).strip('-')
        return anchor

    def _extract_heading(self, content: str):
        """Extract heading title and explicit anchor ID from chapter content."""
        m = re.search(r'^# (.+?)(?:\s*\{#([\w-]+)[^}]*\})?[ \t]*$', content, re.MULTILINE)
        if not m:
            return None, None
        raw_title = m.group(1).strip()
        # Strip any remaining {.class} attrs from title text
        title = re.sub(r'\s*\{[^}]*\}', '', raw_title).strip()
        anchor = m.group(2) if m.group(2) else self._heading_to_anchor(title)
        return title, anchor

    def _assemble_ebook_manuscript(self) -> str:
        """Assemble manuscript with ebook-specific ordering.

        Moves unnumbered front-matter sections (About the Author, etc.)
        to back matter so KDP doesn't treat them as Chapter 1.
        Prepends a markdown TOC with internal links for Kindle navigation.
        """
        front_chapters = []
        story_chapters = []

        for chapter in self.book.chapters:
            is_unnumbered = chapter.is_unnumbered
            if not is_unnumbered:
                if re.search(r'^# .+\{[^}]*\.unnumbered[^}]*\}', chapter.content, re.MULTILINE):
                    is_unnumbered = True

            if is_unnumbered and not chapter.is_epilogue:
                front_chapters.append(chapter)
            else:
                story_chapters.append(chapter)

        ordered = story_chapters + front_chapters

        # Build markdown TOC with internal links
        toc_entries = []
        for chapter in ordered:
            title, anchor = self._extract_heading(chapter.content)
            if not title:
                continue
            if 'about the author' in title.lower():
                continue
            toc_entries.append(f'[{title}](#{anchor})')

        toc_page = '# Table of Contents {.unnumbered}\n\n'
        toc_page += '\n\n'.join(toc_entries)
        toc_page += '\n\n\\newpage\n\n'

        # Assemble chapters
        parts = [toc_page]
        for i, chapter in enumerate(ordered):
            if i > 0:
                parts.append('\n\n\\newpage\n\n')
            parts.append(chapter.content)

        return '\n'.join(parts)

    def build(self, verbose: bool = False) -> str:
        self.check_pandoc()
        self.ensure_output_dir()

        manuscript = self._assemble_ebook_manuscript()
        manuscript_file = self.write_temp_manuscript(manuscript)

        output_file = self.output_path('ebook')

        args = [
            '--to', 'docx',
            '--lua-filter', self.get_lua_filter_path('pagebreak.lua'),
            '--metadata', f'title={self.config.title}',
            '--metadata', f'author={self.config.author}',
        ]

        if self.config.subtitle:
            args += ['--metadata', f'subtitle={self.config.subtitle}']

        args += ['--output', output_file]

        self.run_pandoc(args, manuscript_file, verbose=verbose)

        try:
            os.unlink(manuscript_file)
        except OSError:
            pass

        return output_file
