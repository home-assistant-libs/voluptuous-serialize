from setuptools import setup

setup(name='voluptuous-serialize',
      version='2.2.0',
      description='Convert voluptuous schemas to dictionaries',
      url='http://github.com/balloob/voluptuous-serialize',
      author='Paulus Schoutsen',
      author_email='Paulus@PaulusSchoutsen.nl',
      license='Apache License 2.0',
      install_requires=['voluptuous'],
      packages=['voluptuous_serialize'],
      zip_safe=True)
