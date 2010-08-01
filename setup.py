from setuptools import setup

version = '0.2dev'

long_description = '\n\n'.join([
    open('README.txt').read(),
    open('TODO.txt').read(),
    open('CHANGES.txt').read(),
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
