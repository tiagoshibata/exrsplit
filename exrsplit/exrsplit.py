"""Splitter and merger for multi-view, multi-layer OpenEXR files."""

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
# single-view files. Data channels (such as shadows and Z) are saved as a
# grayscale image. RGB color channels can be saved as separate files per channel
# or merged into RGB images.
#
# The following channels are identified (in upper or lower case) if they are the
# suffix of the channel name (list taken from OpenEXR documentation at
# http://www.openexr.com/documentation.html and other sources):
# R, G, B, A, red, green, blue, alpha, Z, ZBack, AR, AG, AB, X, Y, depth, data,
# shadows, mask, RY, GY, BY, U, V
# Non-identified channels are saved as grayscale.

import collections
import itertools

_NAME_TO_CHANNEL_TYPE = collections.OrderedDict((
    ('red', 'R'), ('green', 'G'), ('blue', 'B'), ('alpha', 'A'),
    ('zback', 'DATA'), ('depth', 'DATA'), ('data', 'DATA'), ('shadows', 'DATA'),
    ('mask', 'DATA'), ('ar', 'DATA'), ('ag', 'DATA'), ('ab', 'DATA'), ('ry', 'DATA'),
    ('gy', 'DATA'), ('by', 'DATA'), ('x', 'DATA'), ('y', 'DATA'), ('r', 'R'), ('g', 'G'),
    ('b', 'B'), ('a', 'A'), ('z', 'DATA'), ('v', 'DATA'), ('u', 'DATA'),
))


def get_view(header, fullname):
    if 'view' in header:
        return header['view']
    views = header.get('multiView')
    if views is None:
        return None
    if '.' not in fullname and fullname.encode('UTF-8') not in views:
        # Default layer is put in default view
        return views[0]
    viewname = fullname.split('.', 1)[0]
    viewname = viewname.encode('UTF-8')
    return viewname in views and viewname or views[0]


def _get_layer(view, fullname):
    if view is not None:
        view = view.decode('UTF-8')
    layer_and_channel = fullname.rsplit('.', 1)
    layer = layer_and_channel[0]
    if len(layer_and_channel) < 2 or layer == view:
        # Channel name only, without layer
        return None
    view_prefix = '{}.'.format(view)
    if layer.startswith(view_prefix):
        return layer[len(view_prefix):]
    return layer


def _get_channel_type(channel):
    name = channel.lower()
    layer_type = _NAME_TO_CHANNEL_TYPE.get(name)
    if layer_type is None:
        print('Unknown channel name {} set as data'.format(channel))
        return 'DATA'
    return layer_type


class EXRChannel:
    """Stores view and layer associated to a channel.

    Non-color channels (eg. Z, shadows) are saved as grayscale images.
    """

    def __init__(self, header, fullname):
        """Get channel data for a given layer in an OpenEXR header.

        Sets attibutes view, layer and channel type. view contains the view of
        the layer or None if file has no views. layer contains the layer and
        sublayers names or None if in the default layer. channel_type contains R,
        G, B, A or DATA.
        """
        self.fullname = fullname
        self.view = get_view(header, fullname)
        self.layer = _get_layer(self.view, fullname)
        self.channel = fullname.rsplit('.', 1)[-1]
        self.channel_type = _get_channel_type(self.channel)


def output_file_name(channel):
    """Build name of output file for a given channel."""
    def as_string(sequence):
        if isinstance(sequence, str):
            return sequence
        return sequence.decode('UTF-8')

    components = '.'.join([as_string(x) for x in (channel.view, channel.layer) if x is not None])
    return components or 'default_layer'


def group_channels(channels):
    """Group channels belonging to the same layer."""
    channels = sorted(channels, key=output_file_name)
    return [list(channel_group) for _, channel_group in itertools.groupby(channels, key=output_file_name)]
