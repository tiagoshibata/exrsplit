exrsplit
========
> Split a multi-layer exr image into multiple files

About .exr
-----
.exr files are very useful, with a high compression, support for high quality and multiple layers. However, many programs don't support loading multi-layer, only files with the standard 3 or 4 color channels. This program uses the OpenEXR python implementation to split a multi-layer exr image into many exr images. The output may be either single channel (with 3-4 images for each layer) or RGB/RGBA and the program supports conversion to png using imagemagick.

Usage
-----

### 1. Setting up
On Mac OSX, install Homebrew:
`ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

Install wget with Homebrew:
`brew install wget`

Make sure Pip is installed:
`wget https://bootstrap.pypa.io/get-pip.py`

`sudo python get-pip.py`

### 2. Install openexr

Mac:

`brew install openexr`

Ubuntu:

`sudo apt-get install libopenexr-dev`

### 3. Install Python bindings

Install Python bindings
`sudo pip install OpenEXR`

### 4. Install Imagemagick

Mac:
`brew install imagemagick`

Ubuntu:
`sudo apt-get install imagemagick`

Author
------
Originally written by Tiago Shibata (https://github.com/tiagoshibata).
