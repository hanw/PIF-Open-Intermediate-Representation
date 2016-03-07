#!/usr/bin/env python

from setuptools import setup

setup(
    name='pif_ir',
    version = '0.9.0',
    install_requires=['pyyaml', 'ply', 'pyparsing==1.5.7', 'pydot'],
    packages=[
        'pif_ir',
        'pif_ir/meta_ir',
        'pif_ir/air',
        'pif_ir/air/objects',
        'pif_ir/bir',
        'pif_ir/bir/objects',
        'pif_ir/bir/utils'
    ],
    package_data= {
        'pif_ir/bir' : ['bir_meta.yml'],
        'pif_ir/air' : ['air_meta.yml']
    }
)
