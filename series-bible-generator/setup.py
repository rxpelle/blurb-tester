from setuptools import setup, find_packages

setup(
    name='series-bible-generator',
    version='0.1.0',
    description='Generate, query, validate, and maintain series bibles from manuscripts',
    author='Randy Pellegrini',
    url='https://github.com/rxpelle/series-bible-generator',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'click',
        'rich',
        'anthropic',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
        ],
    },
    entry_points={
        'console_scripts': [
            'series-bible=series_bible_generator.cli:main',
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
    ],
)
