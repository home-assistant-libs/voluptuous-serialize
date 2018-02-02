from setuptools import setup

setup(name='voluptuous-json',
      version='0.1',
      description='Convert voluptuous schemas to JSON',
      url='http://github.com/balloob/voluptuous-json',
      author='Paulus Schoutsen',
      author_email='Paulus@PaulusSchoutsen.nl',
      license='Apache License 2.0',
      install_requires=['voluptuous'],
      packages=['voluptuous_json'],
      zip_safe=True)