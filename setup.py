#!/usr/bin/env python3
from setuptools import setup, find_packages

def parse_requirements(filename):
    lines = [l.strip() for l in open(filename)]
    return [l for l in lines if l and not l.startswith('#')]


setup(
    name='lumix-control',
    version='0.0.1',
    description='Simple python module for lumix cameras',
    author='Michael Hand, Markus Grotz',
    author_email='mhand@fitbit.com, markus.grotz@kit.edu',
    url='https://github.com/markusgrotz/python_lumix_control',
    install_requires=parse_requirements('requirements.txt'),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
)
