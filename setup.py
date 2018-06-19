import os
from setuptools import setup
from distutils.core import Command


setup(
    name='cpi',
    version='0.0.6',
    description="Quickly adjust U.S. dollars for inflation using the Consumer Price Index (CPI)",
    author='Ben Welsh',
    author_email='ben.welsh@gmail.com',
    url='http://www.github.com/datadesk/cpi',
    license="MIT",
    packages=("cpi",),
    include_package_data=True,
    zip_safe=False,  # because we're including static files
    install_requires=("requests",),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ],
)
