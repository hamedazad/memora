"""
Setup script for Memora Memory Assistant
"""

from setuptools import setup, find_packages
import os

# Read the version from version.py
with open('version.py', 'r') as f:
    exec(f.read())

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Memora Memory Assistant - A Django-based memory management application with voice capabilities"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="memora",
    version=__version__,
    description="A Django-based memory management application with voice capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/memora",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Topic :: Communications",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    python_requires=">=3.8",
    keywords="memory assistant voice django speech recognition",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/memora/issues",
        "Source": "https://github.com/yourusername/memora",
        "Documentation": "https://github.com/yourusername/memora/blob/main/README.md",
    },
) 