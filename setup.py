import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

requires = [
    'pyramid',
    ]

setup(name='pyramid_auto_hq',
      version='0.1.1',
      description='pyramid_auto_hq',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Tarzan',
      author_email='hoc3010@gmail.com',
      url='git@github.com:tarzanjw/pyramid_auto_hq.git',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pyramid_auto_hq',
      install_requires=requires,
      )
