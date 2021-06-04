# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='behavex',
    version='1.3.4',
    python_requires='>=3',
    author='Hernan Rey',
    author_email='behavex_users@googlegroups.com',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    description='Agile test wrapper on top of Behave (BDD).',
    entry_points={
        'console_scripts': [
            'behavex = behavex.runner:main',
        ],
    },
    install_requires=[
        'behave==1.2.6',
        'jinja2',
        'configobj',
        'htmlmin',
        'csscompressor',
    ],
)
