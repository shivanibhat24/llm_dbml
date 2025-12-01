"""Setup script for llm-dbml (fallback for older pip versions)"""

from setuptools import setup, find_packages

setup(
    packages=find_packages(where="."),
    package_dir={"": "."},
)
