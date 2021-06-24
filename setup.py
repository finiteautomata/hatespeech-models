from setuptools import setup, find_packages

setup(
    name='hatespeech-models',
    version='0.0.1',
    packages=find_packages(),
    test_suite="tests",
    install_requires=[
        "mongoengine",
        "python-slugify"
    ]
)
