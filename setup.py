"""Package and distribute the library."""
import os
import time

from setuptools import setup
from setuptools_scm.version import guess_next_version


def read(file_name):
    """Read in the supplied file name from the root directory.

    Args:
        file_name (str): the name of the file

    Returns: the content of the file
    """
    this_dir = os.path.dirname(__file__)
    file_path = os.path.join(this_dir, file_name)
    with open(file_path) as f:
        return f.read()


def version_scheme(version):
    """Version scheme hack for setuptools_scm.

    Appears to be necessary to due to the bug documented here: https://github.com/pypa/setuptools_scm/issues/342

    If that issue is resolved, this method can be removed.
    """
    if version.exact:
        return version.format_with("{tag}")
    else:
        _super_value = version.format_next_version(guess_next_version)
        now = int(time.time())
        return _super_value + str(now)


def local_version(version):
    """
    Local version scheme hack for setuptools_scm.

    Appears to be necessary to due to the bug documented here: https://github.com/pypa/setuptools_scm/issues/342

    If that issue is resolved, this method can be removed.
    """
    return ""


setup(
    name="cpi",
    description="Quickly adjust U.S. dollars for inflation using the Consumer Price Index (CPI)",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Ben Welsh",
    author_email="b@palewi.re",
    url="https://palewi.re/docs/cpi/",
    license="MIT",
    packages=("cpi",),
    include_package_data=True,
    zip_safe=False,
    install_requires=(
        "requests",
        "click",
        "python-dateutil",
        "pandas",
    ),
    entry_points="""
        [console_scripts]
        inflate=cpi.cli:inflate
    """,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
    ],
    project_urls={
        "Documentation": "https://palewi.re/docs/cpi/",
        "Maintainer": "https://github.com/palewire",
        "Source": "https://github.com/palewire/cpi",
        "Tracker": "https://github.com/palewire/cpi/issues",
    },
    setup_requires=["setuptools_scm"],
    use_scm_version={"version_scheme": version_scheme, "local_scheme": local_version},
)
