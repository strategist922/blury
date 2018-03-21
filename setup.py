from setuptools import find_packages
from setuptools import setup

setup(name='blury',
      author='Axel Camara',
      author_email='axel.camara@soprasteria.com',
      setup_requires=['setuptools_scm', 'pytest-runner'],
      tests_require=['pytest'],
      use_scm_version={'write_to': 'blury/version.txt'},
      description="Use blury to blur plate licence and person on images",
      package_data={'blury': ['data/models/*.weights', 'data/cfg/*',
                             'data/test/*']},
      packages=find_packages(),
      test_suite = 'tests',
      # include_package_data: to install data from MANIFEST.in
      include_package_data=True,
      scripts=['bin/blury'],
      zip_safe=False)
