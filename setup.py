from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements.txt file
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="matfin",
    version="0.0.1",
    author="Your Name",
    author_email="daniel.rocharuiz@bocconialumni.ot",
    description="A module for corporate finance and valuation of Fixed Income titles in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thegitofdaniel/matfin",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[requirements],
    entry_points={
        "console_scripts": [
            # Define any command-line scripts here
        ],
    },
)
