# -*- coding: utf-8 -*-
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import setup

    def find_packages():
        return []

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='behavex',
    version='4.0.0rc1',
    license="MIT",
    platforms=['any'],
    python_requires='>=3.5',
    author='Hernan Rey',
    author_email='behavex_users@googlegroups.com',
    url='https://github.com/hrcorval/behavex',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    description='Agile testing framework on top of Behave (BDD).',
    long_description_content_type='text/markdown',
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'behavex = behavex.runner:main',
        ],
    },
    install_requires=[
        'behave==1.2.6',
        'behavex-images',
        'jinja2',
        'configobj',
        'htmlmin',
        'csscompressor'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Testing',
    ],
)
