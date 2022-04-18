import os
from setuptools import setup


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


setup(
    name='cpi',
    version='1.0.0',
    description="Quickly adjust U.S. dollars for inflation using the Consumer Price Index (CPI)",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author='Ben Welsh',
    author_email='b@palewi.re',
    url='http://www.github.com/palewire/cpi',
    license="MIT",
    packages=("cpi",),
    include_package_data=True,
    zip_safe=False,  # because we're including static files
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
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    project_urls={
        "Maintainer": "https://github.com/palewire",
        "Source": "https://github.com/palewire/cpi>",
        "Tracker": "https://github.com/palewire/cpi/issues",
    },
)
