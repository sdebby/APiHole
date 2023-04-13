from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'API module for Pi Hole'
LONG_DESCRIPTION = 'Python API module for comunicating with Pi Hole server, including all functions'

# Setting up
setup(
    name="APiHole",
    version=VERSION,
    author="Shmulik Debby",
    author_email="<shmulik.debby@gmail.com>",
    url='https://github.com/sdebby/APiHole',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['logging', 'requests'],
    keywords=['PiHole', 'pi.hole', 'API'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)