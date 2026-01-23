from setuptools import setup, find_packages

setup(
    name="schema_analysis",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "scipy"
    ],
    author="Antigravity",
    description="Analysis tool for schema experiments",
)
