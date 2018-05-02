# -*- coding: utf-8 -*-

import os
import codecs
import sys

from setuptools import setup, find_packages
from setuptools.command.install import install

VERSION = __import__('realm').get_version()
HERE = os.path.dirname(__file__)


def read(*files):
    content = ''
    for f in files:
        content += codecs.open(os.path.join(HERE, f), 'r').read()
    return content


class VerifyTagVersion(install):
    """Verify that the git tag matches version"""
    def run(self):
        tag = os.getenv("CIRCLE_TAG")
        if tag != VERSION:
            info = "Git tag: {} does not match the version of this app: {}".format(
                tag,
                VERSION
            )
            sys.exit(info)


setup(
    name='etools-permissions',
    url='https://github.com/unicef/etools-permissions',
    author='UNICEF',
    author_email='rapidpro@unicef.org',
    description='Permissions handling for eTools',
    version=VERSION,
    long_description=read('README.rst'),
    platforms=['any'],
    license='Apache 2 License',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.rst'],
        'realm': ['realm/*'],
    },
    install_requires=read("requirements/base.txt"),
    cmdclass={"verify": VerifyTagVersion}
)
