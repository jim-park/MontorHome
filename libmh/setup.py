from setuptools import setup

setup(
    name='libmh',
    version='0.1',
    packages=['libmh'],
    url='http://github.com/lnlgit/mh',
    license='',
    author='Jim Park',
    author_email='jim@linuxnetworks.co.uk',
    description='Library for functions related to the Montorhome app',
    install_requires=[
        'twisted',
        'service_identity',
    ],
    zip_safe=False,
)
