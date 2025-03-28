from setuptools import setup, find_packages

setup(
    name="telegra",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "attrs",
        "yarl",
    ],
    python_requires=">=3.7",
)
