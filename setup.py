# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#configuring-your-project
from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'API module for Pi Hole'
LONG_DESCRIPTION = '''Python API module for comunicating with Pi Hole server, including all functions.
See GitHub for usege'''
AUTHOR='Shmulik Debby'
AUTHOR_EMAIL='shmulik.debby@gmail.com'

# Setting up
setup(
    name="APiHole",
    license='MIT',
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url='https://github.com/sdebby/APiHole',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    python_requires='>=3',
    install_requires=['logging', 'requests'],
    keywords=['PiHole', 'pi.hole', 'API'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        'License :: OSI Approved :: MIT License',
    ]
)