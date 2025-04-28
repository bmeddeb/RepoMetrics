#!/usr/bin/env python
"""
Simple setup script for compatibility with traditional Python tooling.
The actual build is handled by Maturin through pyproject.toml.
"""

import os
import subprocess
import sys
from setuptools import setup

if __name__ == "__main__":
    # If this is a development setup, build the Rust extension
    if "develop" in sys.argv or "install" in sys.argv:
        try:
            print("Building Rust extension with Maturin...")
            subprocess.check_call(["maturin", "develop"])
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error building Rust extension: {e}")
            print("Please install maturin: pip install maturin")
            sys.exit(1)

    # Read dependencies from requirements.txt
    with open("requirements.txt") as f:
        requirements = [
            line.strip() for line in f
            if line.strip() and not line.startswith("#")
        ]

    setup(
        name="RepoMetrics",
        version="0.1.0",
        description="High-performance Git blame operations and repository management",
        author="Ben",
        author_email="ben@example.com",
        python_requires=">=3.7",
        install_requires=requirements,
        packages=["RepoMetrics"],
        license="MIT",
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Rust",
            "Topic :: Software Development :: Version Control :: Git",
        ],
    )
