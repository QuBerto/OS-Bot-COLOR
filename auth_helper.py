import os

from Cython.Build import cythonize
from setuptools import Extension, setup


class AuthClientSetup:
    @staticmethod
    def get_extension():
        # Define the path to the conditional .pyx file
        auth_client_pyx_path = os.path.join("src", "utilities", "auth_client.pyx")

        # Check if the conditional .pyx file exists
        if os.path.exists(auth_client_pyx_path):
            return Extension(name="AuthClient", sources=[auth_client_pyx_path], include_dirs=[os.path.join(os.path.dirname(__file__), "src")])
        return None


# Get the extension
extension = AuthClientSetup.get_extension()

# If the extension exists, include it in the setup
if extension:
    setup(name="auth_client", ext_modules=cythonize([extension]), include_dirs=[os.path.join(os.path.dirname(__file__), "src")])
else:
    setup(
        name="auth_client",
        version="0.1",
        description="AuthClient package without Cython extension",
        packages=["auth_client"],
    )
