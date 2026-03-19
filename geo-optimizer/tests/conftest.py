"""Shared test fixtures."""

import os
import pytest

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


@pytest.fixture
def good_blog_post():
    with open(os.path.join(FIXTURES_DIR, 'good_blog_post.md'), 'r') as f:
        return f.read()


@pytest.fixture
def poor_blog_post():
    with open(os.path.join(FIXTURES_DIR, 'poor_blog_post.md'), 'r') as f:
        return f.read()


@pytest.fixture
def book_landing_page():
    with open(os.path.join(FIXTURES_DIR, 'book_landing_page.html'), 'r') as f:
        return f.read()


@pytest.fixture
def page_with_schema():
    with open(os.path.join(FIXTURES_DIR, 'page_with_schema.html'), 'r') as f:
        return f.read()


@pytest.fixture
def page_without_schema():
    with open(os.path.join(FIXTURES_DIR, 'page_without_schema.html'), 'r') as f:
        return f.read()
