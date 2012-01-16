import os
from setuptools import setup

version = '1.10'

sample_config = open(os.path.join('checkoutmanager',
                                  'tests',
                                  'sample.cfg')).readlines()

long_description = '\n\n'.join([
    open('README.rst').read(),
    '\n'.join(['  ' + line.rstrip() for line in sample_config]),
    open('TODO.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

setup(name='checkoutmanager',
      version=version,
      description="",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='http://reinout.vanrees.org',
      license='GPL',
      packages=['checkoutmanager'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          ],
      extras_require = {
          'test': [
              'z3c.testsetup>=0.3',
              'zope.testing',
              ],
          },
      entry_points={
          'console_scripts': [
              'checkoutmanager = checkoutmanager.runner:main',
          ]},
      )
