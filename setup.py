from setuptools import setup, Distribution
from setuptools.command.build_py import build_py
from distutils import dir_util

import os
import sys
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

pkg = ['hft', 'hft.common']
pkg_data = {}
if '--market' in sys.argv:
    pkg.append('hft.market')
    pkg_data['hft.market'] = ['market.dll']
    sys.argv.pop(sys.argv.index('--market'))
    
    

if '--trade' in sys.argv:
    pkg.append('hft.trade')
    pkg_data['hft.trade'] = ['trade.dll']
    sys.argv.pop(sys.argv.index('--trade'))

if '--all' in sys.argv:
    pkg.append('hft.trade')
    pkg.append('hft.market')
    pkg_data['hft.trade'] = ['trade.dll']
    pkg_data['hft.market'] = ['market.dll']
    sys.argv.pop(sys.argv.index('--all'))

# pre-clean
try:
    dir_util.remove_tree('build')
    dir_util.remove_tree('dist')
    dir_util.remove_tree('hft.egg-info')
except:
    print("not full clean or directories not exist")

setup(
    name="hft",
    version="2.0.0",
    packages=pkg,
    package_data=pkg_data,
    install_requires=['tornado', 'redis'],
    distclass=BinaryDistribution,
    cmdclass=dict(build_py=custom_build_pyc)
)
