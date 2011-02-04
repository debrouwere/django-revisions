import os
import subprocess
from setuptools import setup, find_packages

version = '0.3'
README = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(README).read()
setup(name='django-revisions',
      version=version,
      description=("Implements a revision trail for model instances in Django."),
      long_description=long_description,
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      keywords='revisions versioning history',
      author='Stijn Debrouwere',
      author_email='stijn@stdout.be',
      url='http://stdbrouw.github.com/django-revisions/',
      download_url='http://www.github.com/stdbrouw/django-revisions/tarball/master',
      license='BSD',
      packages=find_packages(),
      )
