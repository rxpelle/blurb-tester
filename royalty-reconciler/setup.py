from setuptools import setup, find_packages

setup(
    name='royalty-reconciler',
    version='0.1.0',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'click>=8.0',
        'rich>=13.0',
        'python-dotenv>=1.0',
        'requests>=2.28',
    ],
    extras_require={
        'dev': ['pytest', 'pytest-cov'],
    },
    entry_points={
        'console_scripts': [
            'royalty-reconciler=royalty_reconciler.cli:main',
        ],
    },
)
