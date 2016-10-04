import collections
import exrsplit.exrsplit as exrsplit
import pytest
import sys

if sys.version_info < (3, 0):
    from itertools import izip_longest as zip_longest
else:
    from itertools import zip_longest


@pytest.mark.parametrize('header,fullname,expected_view', [
    ({}, '', None),
    ({'view': b'camera'}, 'R', b'camera'),
    ({'multiView': [b'left', b'right']}, 'R', b'left'),
    ({'multiView': [b'left', b'right']}, 'car.R', b'left'),
    ({'multiView': [b'left', b'right']}, 'right.B', b'right'),
    ({'multiView': [b'left', b'right']}, 'right.window.R', b'right'),
])
def test_get_view(header, fullname, expected_view):
    assert exrsplit.get_view(header, fullname) == expected_view


@pytest.mark.parametrize('view,fullname,expected_layer', [
    (None, 'R', None),
    (None, 'car.R', 'car'),
    (None, 'window.B', 'window'),
    (None, 'car.window.R', 'car.window'),
    (b'left', 'R', None),
    (b'left', 'right.R', 'right'),
    (b'right', 'right.R', None),
    (b'right', 'right.car.R', 'car'),
])
def test__get_layer(view, fullname, expected_layer):
    assert exrsplit._get_layer(view, fullname) == expected_layer


@pytest.mark.parametrize('fullname,expected_channel_type', [
    ('R', 'R'),
    ('r', 'R'),
    ('B', 'B'),
    ('shadows', 'DATA'),
    ('Z', 'DATA'),
    ('unknown', 'DATA'),
])
def test__get_channel_type(fullname, expected_channel_type):
    assert exrsplit._get_channel_type(fullname) == expected_channel_type

ChannelData = collections.namedtuple('ChannelData', ['view', 'layer', 'channel', 'channel_type'])


@pytest.mark.parametrize('header,fullname,expected_channel', [
    (
        {'multiView': [b'left', b'right']},
        'R',
        ChannelData(view=b'left', layer=None, channel='R', channel_type='R'),
    ),
    (
        {'multiView': [b'left', b'right']},
        'car.R',
        ChannelData(view=b'left', layer='car', channel='R', channel_type='R'),
    ),
    (
        {'multiView': [b'left', b'right']},
        'right.B',
        ChannelData(view=b'right', layer=None, channel='B', channel_type='B'),
    ),
    (
        {'multiView': [b'left', b'right']},
        'right.window.depth',
        ChannelData(view=b'right', layer='window', channel='depth', channel_type='DATA'),
    ),
])
def test_EXRChannel(header, fullname, expected_channel):
    channel = exrsplit.EXRChannel(header, fullname)
    assert ([channel.view, channel.layer, channel.channel, channel.channel_type] ==
            [expected_channel.view, expected_channel.layer, expected_channel.channel, expected_channel.channel_type])


@pytest.mark.parametrize('channel,expected_file_name', [
    (exrsplit.EXRChannel({'multiView': [b'left', b'right']}, 'car.G'), 'left.car'),
    (exrsplit.EXRChannel({}, 'window.depth'), 'window'),
    (exrsplit.EXRChannel({'multiView': [b'left', b'right']}, 'right.window.depth'), 'right.window'),
])
def test_output_file_name(channel, expected_file_name):
    assert exrsplit.output_file_name(channel) == expected_file_name


@pytest.mark.parametrize('channels,expected_groups', [
    ([
        exrsplit.EXRChannel({'multiView': [b'left', b'right']}, 'car.G'),
        exrsplit.EXRChannel({'multiView': [b'left', b'right']}, 'window.G'),
        exrsplit.EXRChannel({'multiView': [b'left', b'right']}, 'car.R'),
    ], [{'left.car.G', 'left.car.R'}, {'left.window.G'}]),
    ([
        exrsplit.EXRChannel({}, 'car.window.G'),
        exrsplit.EXRChannel({}, 'window.G'),
        exrsplit.EXRChannel({}, 'car.R'),
    ], [{'car.R'}, {'car.window.G'}, {'window.G'}]),
])
def test_group_channels(channels, expected_groups):
    groups = exrsplit.group_channels(channels)
    for group, expected_group in zip_longest(groups, expected_groups):
        assert {'{}.{}'.format(exrsplit.output_file_name(x), x.channel) for x in group} == expected_group
