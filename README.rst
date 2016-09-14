exrsplit
========

    Split a multi-layer exr image into multiple files

About OpenEXR
-------------

OpenEXR is an advanced image format supporting high dynamic range
(including floating point up to 64 bits wide), multiple layers (required
for depth data or stereo images) and lossless or lossy compression.
However, many programs don't support loading multi-layer files, only
files with the standard 3 or 4 color channels.

This program uses the OpenEXR Python implementation to split a
multi-layer exr image into many exr images. The output may be either
single channel (with 3-4 images for each layer) or RGB/RGBA. Conversion
to PNG is supported using imagemagick (note, however, that the high
dynamic range is lost when mapped to 24-bit colors). Some nonstandard
naming schemes are also detected and handled.

All layer names cited in the
`documentation <http://www.openexr.com/documentation.html>`__ are
supported:

::

    R, G, B, A, red, green, blue, alpha, Z, ZBack, AR, AG, AB, X, Y, depth, data, shadows, mask, RY, GY, BY, U, V

Layers with unknown names are split to a separate file with a single
data channel.

The program was primarily designed to work with Blender EXR output. It
is tested against Blender output and automatically tested against the
`OpenEXR collection of
images <https://github.com/openexr/openexr-images>`__ with `Travis
CI <https://travis-ci.org/>`__. It should work with any valid OpenEXR
image.

If you find bugs or have a feature request, read
`REPORTING.md <REPORTING.md>`__.

Usage
-----

1. Setting up on Mac OSX
~~~~~~~~~~~~~~~~~~~~~~~~

Thanks `jakecoppinger <https://github.com/jakecoppinger>`__ for Mac
instructions.

Install Homebrew:
``ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"``

Install wget with Homebrew: ``brew install wget``

Make sure Pip is installed:
``wget https://bootstrap.pypa.io/get-pip.py``,
``sudo python get-pip.py``

Install openexr and imagemagick: ``brew install openexr``,
``brew install imagemagick --with-openexr``

Install Python bindings: ``sudo pip install OpenEXR``

1. Setting up on Linux
~~~~~~~~~~~~~~~~~~~~~~

Install the development packages for OpenEXR, the python bindings and
imagemagick.

In Ubuntu, the packages libopenexr-dev, python, python-setuptools and
imagemagick should make it:
``sudo apt-get install libopenexr-dev python python-setuptools imagemagick``.

The Python bindings can be installed with ``easy_install -U openexr``.

Bugs
----

-  The Python binding has issues with luminance Y RY BY encoding with
   sampling rates different to 2.
-  Imagemagick crashes with some EXR images. Calling an external program
   isn't the best solution and I should be using something like `passing
   OpenEXR data to Python Imaging
   Library <http://excamera.com/articles/26/doc/intro.html>`__ to get
   the work done.

Author
------

Originally written by Tiago Shibata (https://github.com/tiagoshibata).
