from setuptools import setup, find_packages

setup(
    name='read-through-calc',
    version='0.1.0',
    packages=find_packages(),
    python_requires='>=3.9',
    install_requires=[
        'click>=8.0',
        'rich>=13.0',
        'python-dotenv>=1.0',
    ],
    extras_require={
        'dev': ['pytest', 'pytest-cov'],
    },
    entry_points={
        'console_scripts': [
            'read-through-calc=read_through_calc.cli:main',
        ],
    },
)
