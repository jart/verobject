# http://packages.python.org/distribute/setuptools.html
# http://diveintopython3.org/packaging.html
# http://wiki.python.org/moin/CheeseShopTutorial
# http://pypi.python.org/pypi?:action=list_classifiers

from ez_setup import use_setuptools
use_setuptools(version="0.6c11")

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name                 = "verobject",
    version              = __import__("verobject").__version__,
    description          = "Version controlled object database on Redis",
    long_description     = read("README.rst"),
    author               = "Justine Tunney",
    author_email         = "jtunney@lobstertech.com",
    url                  = "https://github.com/jart/verobject",
    license              = "MIT",
    install_requires     = ["redis"],
    py_modules           = ["verobject"],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Database",
    ],
)
