try:
    from setuptools import setup
    using_setuptools = True
except ImportError:
    from distutils.core import setup
    using_setuptools = False

from distutils.command.build_py import build_py


setup(
    name="groupcam",
    version='0.5',
    author="Konstantin Alexandrov",
    author_email="iwuvjhdva@gmail.com",
    description="",
    url="https://hg.socio2.net/groupcam/",
    dependency_links=[
        'git+https://github.com/iwuvjhdva/v4l2.git@master#egg=v4l2',
        'git://git.cairographics.org/git/pycairo@master#egg=pycairo',
    ],
    install_requires=[
        'pyyaml',
        'pycairo',
        'v4l2',
        'colander==0.9.9',
        'motor==0.1.2',
        'tornado==3.2',
        'pytest==2.5.2',
        'numpy',
    ],
    packages=['groupcam', 'groupcam.tt4', 'groupcam.api'],
    package_data={
        'groupcam': ['misc/*.*'],
    },
    entry_points={
        'console_scripts': [
            'groupcam = groupcam.main:main',
        ],
    },
    scripts=([] if using_setuptools else ['bin/groupcam']),
    cmdclass=dict(build_py=build_py)
)
