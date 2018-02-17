#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name="sheet2jpk_vat",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Polish",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    description="JPK_VAT report generator (Polish business activity monthly report)",
    license="MIT",
    long_description='See: http://www.finanse.mf.gov.pl/pp/jpk',
    url="https://github.com/tomaszhlawiczka/sheet2jpk_vat",
    project_urls={
        "Documentation": "http://www.finanse.mf.gov.pl/pp/jpk",
        "Source Code": "https://github.com/tomaszhlawiczka/sheet2jpk_vat",
    },

    author="Tomasz Hławiczka",
    author_email="at@tru.pl",

    setup_requires=["setuptools_scm"],
    use_scm_version=True,

    install_requires=["ezodf>=0.3.2", "lxml>=4.1.1", "python-stdnum>=1.8.1", "xmlwitch>=0.3"],
    extras_require={
        "PySide": ["PySide>=1.2.4"]
    },
    entry_points={
        'console_scripts': ['sheet2jpk_vat = sheet2jpk_vat:main']
    }
)
