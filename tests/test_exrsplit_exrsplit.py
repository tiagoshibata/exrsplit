import collections
import exrsplit.exrsplit as exrsplit
import itertools
import pytest


@pytest.mark.parametrize('header,fullname,expected_view', [
    ({}, '', None),
    ({'view': 'camera'}, 'R', 'camera'),
    ({'multiView': ['left', 'right']}, 'R', 'left'),
    ({'multiView': ['left', 'right']}, 'car.R', 'left'),
    ({'multiView': ['left', 'right']}, 'right.B', 'right'),
    ({'multiView': ['left', 'right']}, 'right.window.R', 'right'),
])
def test__get_view(header, fullname, expected_view):
    assert exrsplit._get_view(header, fullname) == expected_view


@pytest.mark.parametrize('view,fullname,expected_layer', [
    (None, 'R', None),
    (None, 'car.R', 'car'),
    (None, 'window.B', 'window'),
    (None, 'car.window.R', 'car.window'),
    ('left', 'R', None),
    ('left', 'right.R', 'right'),
    ('right', 'right.R', None),
    ('right', 'right.car.R', 'car'),
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
        {'multiView': ['left', 'right']},
        'R',
        ChannelData(view='left', layer=None, channel='R', channel_type='R'),
    ),
    (
        {'multiView': ['left', 'right']},
        'car.R',
        ChannelData(view='left', layer='car', channel='R', channel_type='R'),
    ),
    (
        {'multiView': ['left', 'right']},
        'right.B',
        ChannelData(view='right', layer=None, channel='B', channel_type='B'),
    ),
    (
        {'multiView': ['left', 'right']},
        'right.window.depth',
        ChannelData(view='right', layer='window', channel='depth', channel_type='DATA'),
    ),
])
def test_EXRChannel(header, fullname, expected_channel):
    channel = exrsplit.EXRChannel(header, fullname)
    assert ([channel.view, channel.layer, channel.channel, channel.channel_type] ==
            [expected_channel.view, expected_channel.layer, expected_channel.channel, expected_channel.channel_type])


@pytest.mark.parametrize('channel,expected_file_name', [
    (exrsplit.EXRChannel({'multiView': ['left', 'right']}, 'car.G'), 'left.car'),
    (exrsplit.EXRChannel({}, 'window.depth'), 'window'),
    (exrsplit.EXRChannel({'multiView': ['left', 'right']}, 'right.window.depth'), 'right.window'),
])
def test_output_file_name(channel, expected_file_name):
    assert exrsplit.output_file_name(channel) == expected_file_name


@pytest.mark.parametrize('channels,expected_groups', [
    ([
        exrsplit.EXRChannel({'multiView': ['left', 'right']}, 'car.G'),
        exrsplit.EXRChannel({'multiView': ['left', 'right']}, 'window.G'),
        exrsplit.EXRChannel({'multiView': ['left', 'right']}, 'car.R'),
    ], [{'left.car.G', 'left.car.R'}, {'left.window.G'}]),
    ([
        exrsplit.EXRChannel({}, 'car.window.G'),
        exrsplit.EXRChannel({}, 'window.G'),
        exrsplit.EXRChannel({}, 'car.R'),
    ], [{'car.R'}, {'car.window.G'}, {'window.G'}]),
])
def test_group_channels(channels, expected_groups):
    groups = exrsplit.group_channels(channels)
    for group, expected_group in itertools.izip_longest(groups, expected_groups):
        assert {'{}.{}'.format(exrsplit.output_file_name(x), x.channel) for x in group} == expected_group
