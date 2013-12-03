exrsplit - Split a multi-layer exr image into multiple files

.exr files are very useful, with a high compression, support for high quality and multiple layers.
However, many programs don't support loading multi-layer, only files with the standard 3 or 4 color
channels. This program uses the OpenEXR python implementation to split a multi-layer exr image into
many exr images. The output may be either single channel (with 3-4 images for each layer) or RGB/RGBA
and the program supports conversion to png using imagemagick.

To use the program, install the development packages for OpenEXR, the python interface and imagemagick.
In Ubuntu, the packages libopenexr-dev, python, python-setuptools and imagemagick should make it.
Then install the python interface with "easy_install -U openexr".

The program was designed to work with Blender EXR output and tested with them, but should work with
files from other programs, too. If you find bugs, add an issue in github :)

Future plans: rewrite in C++ with multi-core conversion of the images.
