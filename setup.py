import os
from setuptools import setup

setup(
    name = "stplanpy",
    version = "0.1.0",
    author = "Arnout Boelens",
    author_email = "ampboelens@gmail.com",
    packages = ["stplanpy"],
    install_requires=[
        "numpy",
        "shapely",
        "pandas",
        "pandas-flavor",
        "geopandas",
    ],
    description = (
        "The Sustainable Transportation Planner for Python is a library "
        "focused on active transportation and transit. It was inspired "
        "by the stplanr library for R"
    ),
    license = "GPL-3.0",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
    ],
)
