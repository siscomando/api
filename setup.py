# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

requirements = open('requirements.txt', 'r')
requirements = requirements.readlines()

setup(
    name='SisComandoRESTful',
    version='0.0.1',
    author='SisComando Team',
    author_email='horacioibrahim@gmail.com',
    packages=find_packages('siscomando_api'),
    package_dir={'': 'siscomando_api'},
    url='https://github.com/SisComandoRESTful',
    download_url='https://github.com/SisComandoRESTful/webapp/tarball/master',
    description='API RESTful for Siscomando app',
    install_requires=requirements,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
  ],
  keywords=['siscomando', 'eve']
)
