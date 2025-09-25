from setuptools import setup, find_packages

setup(
    name="spike_selection",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.7",
    description="A package for spike selection analysis",
    entry_points={
        "console_scripts": ["greedy-select=spike_selection.cli:main"],
    },
)
