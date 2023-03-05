#!/usr/bin/env python3
# encoding: utf8

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

EXTENSIONS = [
    Extension("app_plugin", ["app_plugin.py"]),
    Extension("app_utils/*", ["app_utils/*.py"]),
    Extension("backend_models/*", ["backend_models/*.py"]),
    Extension("controller/*", ["controller/*.py"]),
    Extension("MongoDB/*", ["MongoDB/*.py"]),        
]

setup(
    name="Web backend",
    ext_modules=cythonize(EXTENSIONS)
)

#>> pip3 install cython
#>> python3 setup.py build_ext --inplace