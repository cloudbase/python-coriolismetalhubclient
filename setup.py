#!/usr/bin/env python3

from setuptools import find_packages
from setuptools import setup

PROJECT = 'coriolis-metal-hub'
VERSION = '0.1'
long_description = ''

setup(
    name=PROJECT,
    version=VERSION,

    description='Coriolis Metal Hub CLI',
    long_description=long_description,

    author='Gabriel Adrian Samfira',
    author_email='gsamfira@cloudbasesolutions.com',

    url='https://github.com/cloudbase/python-coriolismetalhubclient',
    download_url='https://github.com/cloudbase/python-coriolismetalhubclient/tarball/main',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=[
        'cliff',
        'keystoneauth1',
        'requests',
        'six',
        'urllib3'
    ],

    namespace_packages=[],
    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'coriolis-metal-hub = coriolismetalhub.main:main'
        ],
        'coriolismetalhub.cli': [
            'server_list = coriolismetalhub.server:Servers',
            'server_show = coriolismetalhub.server:ShowServer',
            'server_add = coriolismetalhub.server:CreateServer',
            'server_remove = coriolismetalhub.server:RemoveServer',
            'snapshot_list = coriolismetalhub.snapshots:ListSnapshots',
            'snapshot_show = coriolismetalhub.snapshots:ShowSnapshot',
            'snapshot_create = coriolismetalhub.snapshots:CreateSnapshot',
            'snapshot_delete = coriolismetalhub.snapshots:DeleteSnapshot',
        ],
    },

    zip_safe=False,
)
