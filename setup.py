# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='behavex',
    version='1.5.0',
    python_requires='>=3, !=3.9.*',
    author='Hernan Rey',
    author_email='behavex_users@googlegroups.com',
    url='https://github.com/hrcorval/behavex',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    description='Agile test wrapper on top of Behave (BDD).',
    long_description_content_type='text/markdown',
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
    classifiers=[
        'Development Status :: 4 - Beta',
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
        'Topic :: Software Development :: Testing',
    ],
)
