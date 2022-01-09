import setuptools

with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="blackjack21",
    version="0.0.1",
    author="Rahul Nanwani",
    author_email="rahulnanwani@icloud.com",
    description="A complete package for blackjack, with max 5 players on a table, double down, and split features too.",
    long_description=long_description,
    long_description_content_type="text/restructuredtext",
    url="https://github.com/rahul-nanwani/blackjack21/wiki",
    project_urls={
        "Bug Tracker": "https://github.com/rahul-nanwani/blackjack21/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Intended Audience :: Developers"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
