#!/usr/bin/env python3
"""
Setup script for DevSync
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version from version.txt if it exists
version_file = Path("version.txt")
if version_file.exists():
    version = version_file.read_text().strip()
else:
    version = "0.1.0"

# Read README for long description
readme_file = Path("README.md")
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# Read requirements
requirements_file = Path("requirements.txt")
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="devsync",
    version=version,
    author="DevSync Team",
    author_email="devsync@example.com",
    description="Lightweight deployment automation tool - Git deploy, but smart",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/deploy-automation",
    py_modules=["deploy", "deploy_ui"],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "devsync=deploy:main",
            "devsync-ui=deploy_ui:main",
            "deploy=deploy:main",  # backward compatibility
            "deploy-ui=deploy_ui:main",  # backward compatibility
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    keywords="deployment automation ci-cd versioning git github-actions",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/deploy-automation/issues",
        "Source": "https://github.com/yourusername/deploy-automation",
        "Documentation": "https://github.com/yourusername/deploy-automation/wiki",
    },
)