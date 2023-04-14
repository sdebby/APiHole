# https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#configuring-your-project
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description1 = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'API module for Pi Hole'
LONG_DESCRIPTION = 'Python API module for comunicating with Pi Hole server, including all functions.'
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
    long_description=long_description1,
    packages=find_packages(),
    install_requires=['requests'],
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