# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="psws-zendo",
    version="0.0.6",
    author="Aidan Montare",
    author_email="aidan.montare@case.edu",
    description="Zenodo upload for the HamSCI PSWS project and those running fldigi at home",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aidanmontare-edu/psws-zenodo",
    project_urls={
        "Parent Project": "https://hamsci.org/",
        "Source": "https://github.com/aidanmontare-edu/psws-zenodo",
    },
    packages=setuptools.find_packages(),
    scripts=["zenodo-upload.py"],
    keywords="hamsci zenodo hamsci-psws",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Ham Radio",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Atmospheric Science"
    ],
    python_requires='>=3.5',
)