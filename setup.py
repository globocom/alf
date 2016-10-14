# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='alf',
    version='0.7.1',
    description="OAuth Client",
    long_description=open('README.rst').read(),
    keywords='oauth client client_credentials requests',
    author=u'Globo.com',
    author_email='timecore@corp.globo.com',
    url='https://github.com/globocom/alf',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        ],
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
