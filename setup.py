#!/usr/bin/env python
import codecs
import os
import sys
from shutil import rmtree

from setuptools import Command, find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

about = {}

with open(os.path.join(here, "responder", "__version__.py")) as f:
    exec(f.read(), about)

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

required = [
    "starlette==0.13.*",
    "uvicorn[standard]>=0.12.0,<0.24.0.post1",
    "aiofiles",
    "pyyaml",
    "requests",
    "graphene<3.0",
    "graphql-server-core>=1.1",
    "jinja2",
    "rfc3986",
    "python-multipart",
    "chardet",
    "apispec>=1.0.0b1",
    "marshmallow",
    "whitenoise",
    "docopt",
    "requests-toolbelt",
    "itsdangerous",
]


# https://pypi.python.org/pypi/stdeb/0.8.5#quickstart-2-just-tell-me-the-fastest-way-to-make-a-deb
class DebCommand(Command):
    """Support for setup.py deb"""

    description = "Build and publish the .deb package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print(f"\033[1m{s}\033[0m")

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "deb_dist"))
        except FileNotFoundError:
            pass
        self.status("Creating debian manifest…")
        os.system(
            "python setup.py --command-packages=stdeb.command sdist_dsc -z artful --package3=pipenv --depends3=python3-virtualenv-clone"
        )
        self.status("Building .deb…")
        os.chdir("deb_dist/pipenv-{}".format(about["__version__"]))
        os.system("dpkg-buildpackage -rfakeroot -uc -us")


class UploadCommand(Command):
    """Support setup.py publish."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print(f"\033[1m{s}\033[0m")

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except FileNotFoundError:
            pass
        self.status("Building Source distribution…")
        os.system(f"{sys.executable} setup.py sdist bdist_wheel")
        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")
        self.status("Pushing git tags…")
        os.system("git tag v{}".format(about["__version__"]))
        os.system("git push --tags")
        sys.exit()


setup(
    name="responder",
    version=about["__version__"],
    description="A sorta familiar HTTP framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Kenneth Reitz",
    author_email="me@kennethreitz.org",
    url="https://github.com/kennethreitz/responder",
    packages=find_packages(exclude=["tests"]),
    entry_points={"console_scripts": ["responder=responder.cli:cli"]},
    package_data={},
    python_requires=">=3.8",
    setup_requires=[],
    install_requires=required,
    extras_require={},
    include_package_data=True,
    license="Apache 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    cmdclass={"upload": UploadCommand, "deb": DebCommand},
)
