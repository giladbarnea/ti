#!/usr/bin/env python
import io
import sys

from setuptools import find_packages, setup


def read(*filenames, **kwargs):
    encoding = kwargs.get("encoding", "utf-8")
    sep = kwargs.get("sep", "\n")
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


testing = bool({"pytest", "test"}.intersection(sys.argv))

setup(
        name="ti",
        version="0.0.1",
        author="Gilad Barnea",
        author_email="giladbrn@gmail.com",
        packages=find_packages(),
        include_package_data=True,
        scripts=[],
        url="https://github.com/giladbarnea/ti",
        description="Not a silly simple time tracker",
        long_description=read("README.rst", "CHANGES.rst"),
        entry_points={
            "console_scripts": [
                "tf = ti:main",
                ]
            },
        install_requires=['arrow>=1.1.0,<2.0.0', 'toml>=0.10,<0.11'],
        setup_requires=["pytest-runner"] if testing else [],
        tests_require=["pytest",
                       # "cram", "pytest-cram"
                       ],
        extras_require={
            "docs": ["ghp-import", "pygreen"],
            "dev":  ["IPython", 'rich>=10,<11']
            }
        )
