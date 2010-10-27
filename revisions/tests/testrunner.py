# encoding: utf-8

"""This file mainly exists to allow python setup.py test to work.
Courtesy of Eric Holscher and Gregor Müllegger."""

import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_dir = "/".join(test_dir.split('/')[:-1])
sys.path.insert(0, project_dir)

from django.test.utils import get_runner
from django.conf import settings

def run():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(['revisions'])
    sys.exit(bool(failures))

if __name__ == '__main__':
    run()