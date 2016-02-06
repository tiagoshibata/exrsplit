exrsplit
========
> Split a multi-layer exr image into multiple files

About .exr
-----
.exr files are very useful, with a high compression, support for high quality and multiple layers. However, many programs don't support loading multi-layer, only files with the standard 3 or 4 color channels. This program uses the OpenEXR Python implementation to split a multi-layer exr image into many exr images. The output may be either single channel (with 3-4 images for each layer) or RGB/RGBA and the program supports conversion to png using imagemagick. Some nonstandard naming schemes are also detected and handled.

The program was designed to work with Blender EXR output and tested with them, but should work with files from other programs, too. If you find bugs, add an issue in GitHub :)

Usage
-----

### 1. Setting up on Mac OSX
Install Homebrew:
`ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

Install wget with Homebrew:
`brew install wget`

Make sure Pip is installed:
`wget https://bootstrap.pypa.io/get-pip.py`,
`sudo python get-pip.py`

Install openexr and imagemagick:
`brew install openexr`,
`brew install imagemagick --with-openexr`

Install Python bindings:
`sudo pip install OpenEXR`

### 1. Setting up on Linux
Install the development packages for OpenEXR, the python bindings and imagemagick.

In Ubuntu, the packages libopenexr-dev, python, python-setuptools and imagemagick should make it: `sudo apt-get install libopenexr-dev python python-setuptools imagemagick`.

The python bindings can be installed with `easy_install -U openexr`.

Author
------
Originally written by Tiago Shibata (https://github.com/tiagoshibata).
