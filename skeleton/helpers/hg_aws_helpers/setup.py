"""
Setup script for hg_aws_helpers-q package
"""

from setuptools import find_packages, setup

setup(
    name="hg_aws_helpers-q",
    version="1.1.0",
    description="Librería de utilidades reutilizables para AWS CDK con soporte multi-formato y multi-ambiente",
    author="desarrollo-web",
    packages=find_packages(),
    install_requires=[
        "toml>=0.10.2",
        "pyyaml>=6.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
