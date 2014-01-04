# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='alf',
    version='0.4',
    description="OAuth Client",
    long_description=open('README.rst').read(),
    keywords='oauth client client_credentials requests',
    author=u'Globo.com',
    author_email='timecore@corp.globo.com',
    url='https://github.com/globocom/alf',
    license='Proprietary',
    classifiers=['Intended Audience :: Developers'],
    packages=find_packages(
        exclude=(
            'tests',
        ),
    ),
    include_package_data=True,
    install_requires=[
        'requests>=1.2.3',
    ],
)
