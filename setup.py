"""
Setup configuration for metatft-crawler
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="metatft-crawler",
    version="0.1.0",
    author="albertphan",
    author_email="",
    description="Extract competitive Teamfight Tactics meta data from MetaTFT.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/albertphan/metatft-crawler",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "metatft-crawler=metatft_crawler.cli:main",
        ],
    },
)
