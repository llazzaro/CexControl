import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
]

setup(
    name='CexControl',
    version='0.1',
    description='Python utility to connect to Cex.IO ',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Office/Business :: Financial"
    ],
    author='Eloque',
    author_email='',
    url='',
    keywords='cex api bitcoin',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="cexapi",
)
