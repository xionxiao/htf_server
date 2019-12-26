from setuptools import setup, Distribution
from setuptools.command.build_py import build_py

import os
import py_compile

class custom_build_pyc(build_py):
    def byte_compile(self, files):
        for file in files:
            if file.endswith('.py'):
                py_compile.compile(file)
                os.unlink(file)

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False

setup(
    name="HTF Server",
    version="1.0.0",
    packages=['common', 'trade', 'market'],
    package_data={
        'trade': ['trade.dll'],
        'market': ['market.dll'],
    },
    install_requires=['tornado', 'redis'],
    distclass=BinaryDistribution,
    cmdclass=dict(build_py=custom_build_pyc)
)
