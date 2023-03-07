#!/usr/bin/env python3
# encoding: utf8

from distutils.core import setup,Extension
from Cython.Build import cythonize

EXTENSIONS = [
    Extension("app_plugin", ["app_plugin.py"]),
    Extension("app_utils/*", ["app_utils/*.py"]),  
]

setup(
    ext_modules=cythonize(EXTENSIONS)
)

#>> pip3 install cython
#>> python3 setup.py build_ext --inplace