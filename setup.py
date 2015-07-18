#!/usr/bin/env python
# coding: utf-8


import os
from setuptools import setup, find_packages


THISDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(THISDIR)


VERSION = open("version.txt").readline().strip()
DOWNLOAD_BASEURL = "https://pypi.python.org/packages/source/a/dataserv/"
DOWNLOAD_URL = DOWNLOAD_BASEURL + "dataserv-%s.tar.gz" % VERSION


setup(
    name='dataserv',
    version=VERSION,
    description=('Federated server for getting, pushing,'
                 ' and auditing data on untrusted nodes.'),
    long_description=open("README.rst").read(),
    keywords=(""),
    url='http://storj.io',
    author='Shawn Wilkinson',
    author_email='shawn+dataserv@storj.io',
    license='MIT',
    packages=find_packages(),
    download_url = DOWNLOAD_URL,
    test_suite="tests",
    install_requires=[
        'Flask == 0.10.1',
        'Flask-SQLAlchemy == 2.0',
        'RandomIO == 0.2.1',
        'partialhash == 1.1.0'
    ],
    tests_require=[
        'coverage',
        'coveralls'
    ],
    zip_safe=False,
    classifiers=[
        # "Development Status :: 1 - Planning",
        # "Development Status :: 2 - Pre-Alpha",
        "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
