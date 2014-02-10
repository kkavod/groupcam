# -*- coding: utf-8 -*-

try:
    from setuptools import setup
    using_setuptools = True
except ImportError:
    from distutils.core import setup
    using_setuptools = False

from distutils.command.build_py import build_py


setup(
    name="groupcam",
    version='0.01',
    author="Konstantin Alexandrov",
    author_email="iwuvjhdva@gmail.com",
    description="",
    url="https://hg.socio2.net/groupcam/",
    install_requires=[
        'pycairo',
    ],
    packages=['groupcam', 'groupcam.http'],
    package_data={
    },
    entry_points={
        'console_scripts': [
            'groupcam = groupcam.main:main',
        ],
    },
    scripts=([] if using_setuptools else ['bin/groupcam']),
    cmdclass=dict(build_py=build_py)
)
