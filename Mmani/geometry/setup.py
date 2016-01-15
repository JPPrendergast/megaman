from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os

# in the command line Mmani/Mmani/Geometry
# first set your FLANN path: with e.g. export FLANN_ROOT=/homes/jmcq/flann-1.8.4-src
# then to build: python setup.py build_ext --inplace 

flann_path = os.environ['FLANN_ROOT']   

setup(ext_modules = cythonize(
    Extension(
           "cyflann_index",
           sources=["cyflann_index.pyx","flann_radius_neighbors.cc"],
           language="c++",
           extra_compile_args=["-I" + flann_path + "/src/cpp/"],
    )))