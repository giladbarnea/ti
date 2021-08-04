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
        name="timefred",
        version="0.0.3",
        author="Gilad Barnea",
        author_email="giladbrn@gmail.com",
        packages=find_packages(),
        include_package_data=True,
        scripts=[],
        url="https://github.com/giladbarnea/timefred",
        description="A beautiful and intelligent time tracker",
        long_description=read("README.rst", "CHANGES.rst"),
        entry_points={
            "console_scripts": [
                "tf = timefred.timefred:main",
                ]
            },
        install_requires=['arrow>=1.1.0,<2.0.0',
                          'toml>=0.10,<0.11',
                          'PyYAML>=5.4.1',
                          'pytz>=2021.1'
                          ],
        # setup_requires=["pytest-runner"] if testing else [],
        tests_require=["pytest",
                       # "cram", "pytest-cram"
                       ],
        extras_require={
            # "docs": ["ghp-import", "pygreen"],
            # "dev":  ["IPython", 'rich>=10,<11']
            }
        )
