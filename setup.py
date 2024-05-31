import os

from auth_setup import AuthClientSetup
from Cython.Build import cythonize
from setuptools import Extension, setup

"""
1. Start writing a script just like normal
2. Copy file, and rename extension to .pyx
3. Set path to the .pyx file
4. Setup the name,
5. Ajust modules if needed
6. Run python setup.py build_ext
"""

# Define the path to your main .pyx file
pyx_file_path = os.path.join("src", "model", "osrs", "private", "testing.pyx")

# Define the extension for the main .pyx file
extensions = [Extension(name="Testing", sources=[pyx_file_path], include_dirs=[os.path.join(os.path.dirname(__file__), "src")])]

# Get the auth client extension if it exists
auth_extension = AuthClientSetup.get_extension()
if auth_extension:
    extensions.append(auth_extension)

# Setup the package
setup(name="your_package_name", ext_modules=cythonize(extensions), package_dir={"": "src/model/osrs/private"})
