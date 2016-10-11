exrsplit
========
[![Build Status](https://travis-ci.org/tiagoshibata/exrsplit.svg?branch=master)](https://travis-ci.org/tiagoshibata/exrsplit)
> Split a multi-layer exr image into multiple files


About OpenEXR
-----
OpenEXR is an advanced image format supporting high dynamic range (including floating point up to 64 bits wide), multiple layers, multiple views (required for e.g. stereo images) and lossless or lossy compression. However, many programs don't support loading multi-view/multi-layer files, only files with standard 3 or 4 color channels.

This program uses the OpenEXR Python interface to split a multi-view/multi-layer exr or join multiple images into one image.

Example usage (with a dual-view and multi-layer image from the official [OpenEXR collection of images][openexr-images]):

```
# Create one file per channel and convert data channels
# (eg. depth or mask) to its grayscale representation:
$ python -m exrsplit --split-channels ../Beachball/singlepart.0006.exr
1/20 - Saving 1 channels to right.A.exr
2/20 - Saving 1 channels to right.forward.left.v.exr
3/20 - Saving 1 channels to right.disparityL.y.exr
4/20 - Saving 1 channels to left.Z.exr
...
17/20 - Saving 1 channels to right.whitebarmask.left.mask.exr
18/20 - Saving 1 channels to right.Z.exr
19/20 - Saving 1 channels to right.forward.left.u.exr
20/20 - Saving 1 channels to left.B.exr

# Create one file per layer:
$ python -m exrsplit ../Beachball/singlepart.0006.exr
1/8 - Saving 5 channels to left.exr
2/8 - Saving 5 channels to right.exr
3/8 - Saving 2 channels to right.disparityL.exr
4/8 - Saving 2 channels to right.disparityR.exr
5/8 - Saving 2 channels to right.forward.left.exr
6/8 - Saving 2 channels to right.forward.right.exr
7/8 - Saving 1 channels to right.whitebarmask.left.exr
8/8 - Saving 1 channels to right.whitebarmask.right.exr

# Merge some files. We'll use left and right as view names:
$ ls
left.exr              right.exr                right.whitebarmask.left.exr
right.disparityL.exr  right.forward.left.exr   right.whitebarmask.right.exr
right.disparityR.exr  right.forward.right.exr
$ python -m exrsplit --merge --view right --view left * merged.exr
Using views right, left
1/8 - Merging left.exr
2/8 - Merging right.disparityL.exr
3/8 - Merging right.disparityR.exr
4/8 - Merging right.exr
5/8 - Merging right.forward.left.exr
6/8 - Merging right.forward.right.exr
7/8 - Merging right.whitebarmask.left.exr
8/8 - Merging right.whitebarmask.right.exr
```

All layer names cited in the [documentation](http://www.openexr.com/documentation.html) are supported:

```
R, G, B, A, red, green, blue, alpha, Z, ZBack, AR, AG, AB, X, Y, depth, data, shadows, mask, RY, GY, BY, U, V
```

When using `--split-channels`, layers with unknown names are treated as data channels (a gray scale representation is generated).

The program was initially designed to work with Blender EXR output. It is tested against the [OpenEXR collection of images](https://github.com/openexr/openexr-images) with [Travis CI](https://travis-ci.org/tiagoshibata/exrsplit). It should work with any valid OpenEXR image.

The multi-part specification introduced in OpenEXR 2 is not supported. The OpenEXR Python bindings doesn't support it yet.

If you find bugs or have a feature request, read [REPORTING.md](REPORTING.md).

Usage
-----

### Setting up
This package can be installed with pip: `pip install -U git+https://github.com/tiagoshibata/exrsplit.git@master`. The installation of OpenEXR Python bindings, one of its dependencies, will require OpenEXR libraries and a C++ compiler.

### 1. On Linux
Install pip and the development packages for OpenEXR.

In Ubuntu, the following packages should make it: `sudo apt-get install libopenexr-dev python-pip`. Then run `pip install -U git+https://github.com/tiagoshibata/exrsplit.git@master`.

### 2. On Mac OSX
Thanks [jakecoppinger](https://github.com/jakecoppinger) for Mac instructions.

Install Homebrew:
`ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

Install Python with Homebrew (its version also includes pip) and openexr:
`brew install python openexr`

Run `pip install -U git+https://github.com/tiagoshibata/exrsplit.git@master`.

Issues
-----
* The Python bindings have many issues in its PyPI repository, most notably missing support for channel subsampling and Python3. [The latest git revision should be used](https://github.com/jamesbowman/openexrpython).

* Python 3 support is experimental.

Author
------
Originally written by Tiago Shibata (https://github.com/tiagoshibata).

[openexr-images]: https://github.com/openexr/openexr-images
