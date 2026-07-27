#!/usr/bin/env python3
"""
Setup script para Hetzner MCP Connection
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hetzner-mcp-connection",
    version="1.0.0",
    author="AI Foundry Col",
    author_email="contact@aifoundry.col",
    description="MCP para conectar Mistral Work a los servicios VPS de Hetzner Cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AI-Foundry-Col/hetzner-mcp-connection",
    project_urls={
        "Bug Tracker": "https://github.com/AI-Foundry-Col/hetzner-mcp-connection/issues",
        "Documentation": "https://github.com/AI-Foundry-Col/hetzner-mcp-connection#readme",
        "Source Code": "https://github.com/AI-Foundry-Col/hetzner-mcp-connection",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.5.0",
        "typing-extensions>=4.8.0",
        "python-dotenv>=1.0.0",
        "rich>=13.7.0",
        "click>=8.1.0",
        "tenacity>=8.2.0",
        "aiohttp>=3.8.0",
        "pydantic-settings>=2.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=24.0.0",
            "ruff>=0.1.0",
            "mypy>=1.8.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hetzner-mcp=hetzner_mcp.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Natural Language :: Spanish",
        "Framework :: Pydantic",
        "Typing :: Typed",
    ],
    keywords=[
        "hetzner",
        "mcp",
        "vps",
        "cloud",
        "automation",
        "ai",
        "mistral",
        "nlp",
        "natural-language",
        "spanish",
    ],
    license="MIT",
    license_files=["LICENSE"],
    include_package_data=True,
    package_data={
        "hetzner_mcp": ["py.typed"],
    },
)
