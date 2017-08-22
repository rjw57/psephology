import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
        install_requires = f.read().split()

tests_require = '''
    BeautifulSoup4
    flask-testing
    nose
'''.split()

setup(
    name='psephology',
    packages=find_packages(),
    include_package_data=True,

    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',

    # To allow for setup.py nosetests command
    setup_requires=['nose>=1.0'],

    # Required because we ship static data files (templates, etc) within our
    # package
    zip_safe=False,
)
