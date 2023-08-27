import re

from setuptools import setup

with open('blackjack21/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='blackjack21',
    version=version,
    description='A complete package for blackjack, with no players limit on a table, double down, and split features too.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://blackjack21.rtfd.io/en/latest/',
    project_urls={
        'Documentation': 'https://blackjack21.rtfd.io/en/latest/',
        'Source': 'https://github.com/rahul-nanwani/blackjack21/',
        'Tracker': 'https://github.com/rahul-nanwani/blackjack21/issues'
    },
    author='Rahul Nanwani',
    author_email='rahulnanwani@icloud.com',
    license='MIT',
    packages=['blackjack21'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Games/Entertainment'
    ],
    install_requires=[],
)
