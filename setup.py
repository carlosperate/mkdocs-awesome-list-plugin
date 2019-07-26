# -*- coding: utf-8 -*-
from setuptools import setup

with open("README.md") as f:
    readme = f.read()

setup(
    name="MkDocsAwesomeListPlugin",
    version="0.1.0",
    description="MkDocs Plugin to inject social media cards for each entry in an awesome-list.",
    long_description=readme,
    keywords=["mkdocs", "plugin", "awesome", "list"],
    author="Carlos Pereira Atencio",
    author_email="carlosperate@embeddedlog.com",
    url="https://github.com/carlosperate/mkdocs-awesome-list-plugin",
    license="MIT license",
    packages=["mkdocs_awesome_list_plugin"],
    install_requires=["mkdocs", "webpreview>=1.6.0"],
    python_requires=">=3.4, <4",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    # This entry point is necessary for MkDocs to be able to use the plugin
    entry_points={
        'mkdocs.plugins': [
            'awesome-list = mkdocs_awesome_list_plugin.awesomelist:AwesomeList',
        ]
    },
)
