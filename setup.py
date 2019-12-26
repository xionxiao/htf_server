from setuptools import setup, Distribution
from os import path

here = path.abspath(path.dirname(__file__))

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
    distclass=BinaryDistribution
)
