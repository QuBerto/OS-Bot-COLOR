import os

from Cython.Build import cythonize
from setuptools import Extension, setup

# Define the path to your .pyx file
pyx_file_path = os.path.join("src", "model", "osrs", "private", "testing.pyx")

# Define the extension module
extensions = [Extension(name="Testing", sources=[pyx_file_path], include_dirs=[os.path.join(os.path.dirname(__file__), "src")])]

setup(name="testing", ext_modules=cythonize(extensions), package_dir={"": "src/model/osrs/private"})
