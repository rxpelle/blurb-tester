from setuptools import setup, find_packages

setup(
    name='geo-optimizer',
    version='0.1.0',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'click>=8.0',
        'rich>=13.0',
        'beautifulsoup4>=4.12',
        'requests>=2.28',
    ],
    extras_require={
        'dev': ['pytest', 'pytest-cov'],
    },
    entry_points={
        'console_scripts': [
            'geo-optimizer=geo_optimizer.cli:main',
        ],
    },
)
