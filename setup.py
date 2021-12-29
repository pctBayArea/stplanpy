import os
import pathlib
from setuptools import setup

# The directory containing this file
current_dir = pathlib.Path(__file__).parent

# The text of the README file
README = (current_dir / "README.md").read_text()

setup(
    name = "stplanpy",
    version = "0.2.0",
    author = "Arnout Boelens",
    author_email = "ampboelens@gmail.com",
    packages = ["stplanpy"],
    install_requires=[
        "numpy",
        "shapely<=2.0",
        "pandas",
        "pandas-flavor",
        "geopandas>=0.9",
    ],
    description = (
        "The Sustainable Transportation Planner for Python is a library "
        "focused on active transportation and transit. It was inspired "
        "by the stplanr library for R"
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/pctBayArea/stplanpy",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
    ],
)
