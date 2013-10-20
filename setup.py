import os
from setuptools import setup 

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "crud_config",
    version = "0.1a",
    author = "Richard Maynard",
    author_email = "richard.maynard@[rackspace|gmail].com",
    description = ("A utility library to handle CRUD RestAPI operations"),
    license = "Apache v2.0",
    url = "https://github.com/ephur/crud_config",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)


