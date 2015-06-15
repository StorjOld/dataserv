from setuptools import setup

setup(
    name='dataserv', version='1.0',
    description='Federated server for getting, pushing, and auditing data on untrusted nodes.',
    author='Shawn Wilkinson', author_email='shawn+dataserv@storj.io',
    url='http://storj.io',

    #  Uncomment one or more lines below in the install_requires section
    #  for the specific client drivers/modules your application needs.
    install_requires=['Flask', 'Flask-SQLAlchemy', 'Flask-Testing'],
    tests_require=['coverage', 'coveralls'],
    test_suite="tests",
)
