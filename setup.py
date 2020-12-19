# -*- coding: utf-8 -*-

# Author: Tank Overlord <TankOverLord88@gmail.com>
#
# License: BSD 3-Clause


import setuptools

import diepX

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    required = fh.read().splitlines()

setuptools.setup(
    name="diep-X",
    version=diepX.__version__,
    author="Tank Overlord",
    author_email="TankOverLord88@gmail.com",
    description="A mini tank-shooting game",
    license="BSD 3-Clause",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/tank-overlord/diep-X",
    packages=setuptools.find_packages(),
    classifiers=[  # https://pypi.org/classifiers/
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
    ],
    install_requires=required,
    python_requires='>=3.6',
    include_package_data=True,
)
