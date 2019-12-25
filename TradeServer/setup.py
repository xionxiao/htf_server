from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

pkg = find_packages()
print pkg

setup(
    name="TradeServer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=['tornado'],
    entery_points={
        'console_scripts': []
    }
)
