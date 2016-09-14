#!/usr/bin/python2
# The MIT License (MIT)
#
# Copyright (c) 2016 Tiago Koji Castro Shibata
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Python script to convert a multi-layer exr image into many exr or png images.
#
# EXR images have multiple channels, which specify the components of an image (R,
# G and B for example). It allows "layers", defined as sets of channels that
# logically belong together. They must be named as:
# layername.channel (eg. window.R)
# Many programs will look for default channel names in the default layer and
# accept only channels named R, G, B and A. exrsplit extracts all layer
# information from an EXR image into separate EXR images. It also handles some
# nonstandard naming schemes (read further).
#
# Layers may also be nested, so layers contained in others can be represented
# (so layername = layer[.sublayer]*.channel). For example:
# room.door.R, room.door.G, room.door.B, room.desk.R, room.desk.G, room.desk.B
#
# The specification also supports multi-view files. They allow the description
# of multiple point of view of the same scene in a file. For example, stereo
# images might use left and right channels. The multiView attribute lists views
# in a file. The first one is the view of the default channels. So, for example,
# the image:
# multiView = ['left', 'right'], channels = ['R', 'G', 'B', 'right.R', 'right.G',
# 'right.B']
# Will be parsed to generate the following output:
# left.R left.G left.B right.R right.G right.B
# In a multiview image, all channels must be kept in a view.
#
# Notice that there is no explicit requirement that a multi-layer image has a
# default layer and many programs that support only single layer files won't open
# them. Apparently, the mistake was noticed and fixed for multi-view files (the
# first multiView attribute represents the default layer, which will be kept
# without layer or view prefixes).
#
# exrsplit will split a multi-layer, multi-view file into many single-layer,
# single-view files. Data channels (such as shadows and Z) are saved as a single
# layer grayscale image. RGB color channels can be saved as separate files per
# channel or merged into RGB images.
#
# For files NOT following recommended view and layer naming and separators
# (eg. https://github.com/tiagoshibata/exrsplit/pull/1), the following channels
# are identified (in upper or lower case) if they are the suffix of the channel name
# (list taken from OpenEXR documentation at  http://www.openexr.com/documentation.html
# and other sources):
# R, G, B, A, red, green, blue, alpha, Z, ZBack, AR, AG, AB, X, Y, depth, data,
# shadows, mask, RY, GY, BY, U, V

import OpenEXR
import collections
import copy
import itertools
from sys import argv
from subprocess import Popen


class EXRChannel:
    # How should the channel be interpeted. Non-color channels (Z, shadows...)
    # will be saved as gray images.
    R = 0
    G = 1
    B = 2
    A = 3
    DATA = 4

    # CHANNEL_TYPES_TUPLE stored as lowercase.
    CHANNEL_TYPES_TUPLE = (
        ('red', R), ('green', G), ('blue', B), ('alpha', A),
        ('zback', DATA), ('depth', DATA), ('data', DATA), ('shadows', DATA),
        ('mask', DATA), ('ar', DATA), ('ag', DATA), ('ab', DATA), ('ry', DATA),
        ('gy', DATA), ('by', DATA), ('x', DATA), ('y', DATA), ('r', R), ('g', G),
        ('b', B), ('a', A), ('z', DATA), ('v', DATA), ('u', DATA))
    CHANNEL_TYPES = collections.OrderedDict(CHANNEL_TYPES_TUPLE)

    def __init__(self, name):
        self.original_name = name
        if '.' not in name:
            # Parse as default layer.
            self.parse_suffix_default_layer(name)
        else:
            name_fields = name.split('.')
            layer_channel = name_fields[-1].lower()
            if layer_channel in EXRChannel.CHANNEL_TYPES:
                self.type = EXRChannel.CHANNEL_TYPES[layer_channel]
            else:
                print('Unknown channel name %s saved as data' % (name))
                self.type = EXRChannel.DATA
            self.channel_name = name_fields[-1]
            self.filename = '.'.join(name_fields[0:-1])
        if self.filename:
            self.filename += exr_file_view
        else:
            # If this is part of the default layer, don't add a period before
            # first prefix.
            self.filename = exr_file_view[1:]

    def parse_suffix_default_layer(self, name):
        # For channels in default layer. Some (stupid) programs put all of them
        # in the default layer (see https://github.com/tiagoshibata/exrsplit/pull/1),
        # so some workarouds are necessary.
        lower_name = name.lower()
        if lower_name in EXRChannel.CHANNEL_TYPES:
            # Known channel name.
            self.type = EXRChannel.CHANNEL_TYPES[lower_name]
            self.channel_name = name
        else:
            # Unknown channel name, might be a long layer + channel name without
            # separators.
            for (channel_sufix, channel_type) in EXRChannel.CHANNEL_TYPES.items():
                if lower_name.endswith(channel_sufix):
                    print('Unknown default channel %s assumed to be of type %s' % (name, channel_sufix))
                    self.type = channel_type
                    self.channel_name = channel_sufix
                    self.filename = name[:-len(channel_sufix)]
                    return
            else:
                print('Unknown default channel %s could not be identified' % (name))
                print('Saving as default data channel')
                self.type = EXRChannel.DATA
                self.channel_name = name

        if 'multiView' in exr_header:
            self.filename = exr_header['multiView'][0]
        else:
            self.filename = ''

    def build_output_name(self):
        if self.filename:
            return '%s.%s.exr' % (channel.filename, channel.channel_name)
        # If default layer and no view information, don't add a period before
        # first prefix.
        return '%s.exr' % (channel.channel_name)

    def is_rbga(self):
        return self.type == EXRChannel.R or self.type == EXRChannel.G or \
            self.type == EXRChannel.B or self.type == EXRChannel.A

    def __lt__(self, other):
        # Sort by filename to help identify layers of the same output file.
        return self.filename < other.filename

    def __eq__(self, other):
        return self.filename == other.filename


def usage():
    print('Usage: exrsplit [options] file\n'
          'Options:\n'
          '\t-exr\t\tConvert a multi-layer exr file into multiple exr files (default).\n'
          '\t-png\t\tConvert a multi-layer exr file into multiple png files.\n'
          '\t-m\t\tMerge channels (default)\n'
          '\t-s\t\tSplit channels\n'
          '\t-v\t\tVerbose mode')
    exit(1)


def exr_to_png(image):
    if verbose:
        print('Converting to png')
    Popen('convert %s %spng && rm %s' % (target_file, target_file[:-3], target_file), shell=True)


def write_output_file(filename, header, channels):
    output = OpenEXR.OutputFile(filename, header)
    output.writePixels(channels)
    if output_format == 1:
        exr_to_png(filename)

if len(argv) == 1:
    usage()

output_format = 0    # 0 = exr, 1 = png.
verbose = False
merge = True        # merge channels from the same layer in a single image.


for arg in argv[1:-1]:
    if arg == '-exr':
        output_format = 0
    elif arg == '-png':
        output_format = 1
    elif arg == '-m':
        merge = True
    elif arg == '-s':
        merge = False
    elif arg == '-v':
        verbose = True
    else:
        print('Unknown option: ' + arg)
        usage()


if not OpenEXR.isOpenExrFile(argv[-1]):
    print("Invalid EXR image")
    exit(1)

exr_file = OpenEXR.InputFile(argv[-1])
if not exr_file.isComplete:
    print("Exr file isn't complete (corrupted or some program is still writing to the file?)")
    exit(1)

exr_header = exr_file.header()
if 'view' in exr_header:
    exr_file_view = '.' + exr_header['view']
else:
    exr_file_view = ''

if verbose:
    print('Channels from input file:')
    print(exr_header['channels'])

out_header = copy.deepcopy(exr_header)
del out_header['channels']
if 'view' in out_header:
    del out_header['view']
if 'multiView' in out_header:
    del out_header['multiView']
# Put some comment that this file has been modified.
# suffix = b'Processed by exrsplit'
# if 'comments' in out_header:
#     if suffix not in out_header['comments']:
#         out_header['comments'] += b'-' + suffix
# else:
#     out_header['comments'] = suffix

channels = [EXRChannel(layer) for layer in exr_header['channels']]

# Groups channels belonging to the same file.
grouped_channels = [list(channel_group) for unique_channel, channel_group in itertools.groupby(sorted(channels))]
group_index = 1
for channel_group in grouped_channels:
    channel_index = 1
    out_colored_header = None
    for channel in channel_group:
        if not merge or channel.type == EXRChannel.DATA:
            target_file = channel.build_output_name()
            if verbose:
                print('%s/%s %s/%s - Save layer %s in %s' % (group_index, len(grouped_channels),
                      channel_index, len(channel_group), channel.original_name, target_file))
            out_header['channels'] = {}
            if channel.type == EXRChannel.DATA:
                # Copy pixel format to RGB components (generate grayscale image of data).
                out_header['channels']['R'] = out_header['channels']['G'] = \
                    out_header['channels']['B'] = exr_header['channels'][channel.original_name]
                write_output_file(target_file, out_header, {
                    'R': exr_file.channel(channel.original_name),
                    'G': exr_file.channel(channel.original_name),
                    'B': exr_file.channel(channel.original_name)})
            else:
                out_header['channels'][channel.channel_name] = exr_header['channels'][channel.original_name]
                write_output_file(target_file, out_header, {channel.channel_name: exr_file.channel(channel.original_name)})
        else:
            if verbose:
                print('%s/%s %s/%s - Will merge layer %s' % (group_index, len(grouped_channels),
                    channel_index, len(channel_group), channel.original_name))
            if out_colored_header is None:
                out_colored_header = copy.deepcopy(out_header)
                out_colored_header['channels'] = {}
                colored_channels = {channel.channel_name: exr_file.channel(channel.original_name)}
            else:
                colored_channels[channel.channel_name] = exr_file.channel(channel.original_name)
            out_colored_header['channels'][channel.channel_name] = exr_header['channels'][channel.original_name]
        channel_index += 1
    if out_colored_header is not None:
        # We need to merge color channels.
        if channel.filename:
            target_file = '%s.exr' % (channel.filename)
        else:
            target_file = 'default.exr'
        if verbose:
            print('%s/%s - Merging colors to %s' % (group_index, len(grouped_channels), target_file))
        write_output_file(target_file, out_colored_header, colored_channels)
        del colored_channels

    group_index += 1
