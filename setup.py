from setuptools import setup, find_packages
from psephology.version import __version__

install_requires = '''
    flask
    flask-debugtoolbar
    flask-migrate
    flask-shell-ipython
    flask-sqlalchemy

    sqlalchemy
    sqlalchemy-utils

    future
'''.split()

tests_require = '''
    flask-fixtures
    flask-testing
    nose
    pyyaml
'''.split()

setup(
    name='psephology',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,

    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',

    # To allow for setup.py nosetests command
    setup_requires=['nose>=1.0'],
)
