# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='behavex',
    version='1.2.6',
    python_requires='>=3',
    author='Hernan Rey',
    author_email='hernanrey@gmail.com',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    description='Agile test wrapper on top of Behave (BDD).',
    entry_points={
        'console_scripts': [
            'behavex = behavex.runner:main',
        ],
    },
    install_requires=[
        'requests',
        'behave==1.2.6',
        'jinja2',
        'configobj',
        'openpyxl',
        'beautifulsoup4',
        'htmlmin',
        'csscompressor',
        'lxml',
        'numpy==1.19.3',
        'pillow',
        'markupsafe',
    ],
)
