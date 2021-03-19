"""
Behavex setup module
"""
from setuptools import find_packages, setup

setup(
    name="behavex",
    version="1.2.2",
    python_requires=">=2.7",
    author="Hernan Rey",
    author_email="hernanrey@gmail.com",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    description="Agile testing wrapper based on Behave (BDD)",
    entry_points={
        "console_scripts": [
            "behavex = behavex.runner:main",
        ],
    },
    install_requires=[
        "requests",
        "behave==1.2.6",
        "jinja2",
        "configobj",
        "openpyxl",
        "beautifulsoup4",
        "htmlmin",
        "csscompressor",
        "lxml",
        "numpy==1.19.3",
        "pillow",
        "markupsafe",
    ],
)
