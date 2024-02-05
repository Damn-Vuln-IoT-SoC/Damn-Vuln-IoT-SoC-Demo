#!/usr/bin/env python3

from setuptools import setup
from setuptools import find_packages


setup(
    name="damn-vuln-iot-soc-demo",
    version="1.0",
    description="Demo of the Damn Vuln IoT SoC project",
    author="Adam HENAULT, Seydina Oumar NIANG, Mohamed AFASSI, Philippe TANGUY",
    author_email="henault.adam@gmail.com, philippe.tanguy@univ-ubs.fr",
    download_url="https://sourcesup.renater.fr/projects/liteinjector/",
    python_requires="~=3.6",
    packages=find_packages(exclude=()),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "build_demo=liteinjector.software.liteinjector_cli:main"
        ],
    },
)
