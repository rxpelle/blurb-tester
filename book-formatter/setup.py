from setuptools import setup, find_packages

setup(
    name='book-formatter',
    version='0.1.0',
    description='One command to format your book for every platform',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Randy Pellegrini',
    url='https://github.com/rxpelle/book-formatter',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'click',
        'rich',
        'pyyaml',
        'jinja2',
        'python-docx',
        'ebooklib',
        'Pillow',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
        ],
    },
    entry_points={
        'console_scripts': [
            'book-formatter=book_formatter.cli:main',
        ],
    },
    package_data={
        'book_formatter': [
            'templates/default/*',
            'lua_filters/*',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Office/Business',
        'Topic :: Text Processing :: Markup',
    ],
)
