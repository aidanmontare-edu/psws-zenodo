# -*- coding: utf-8 -*-

import codecs
import os

import setuptools

"""Thanks to pip"""


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            # __version__ = "0.9"
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="psws-zendo",
    version=get_version("zenodo-upload.py"),
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
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    python_requires=">=3.5",
)
