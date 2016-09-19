import collections
import exrsplit.__main__ as exrsplit_main
import pytest

CmdArgs = collections.namedtuple('CmdArgs', ['png', 'split_channels', 'merge', 'image'])


@pytest.mark.parametrize('flags', [
    (CmdArgs(png=False, split_channels=False, merge=True, image=['a', 'b'])),
])
def test_incompatible_flags(flags):
    with pytest.raises(SystemExit):
        exrsplit_main.main(flags)


@pytest.mark.parametrize('header,expected_header', [
    (
        {'view': 'camera', 'moreData': 'someData', 'channels': {'R': '0123'}},
        {'comments': 'Processed by exrsplit', 'moreData': 'someData', 'channels': {}},
    ), (
        {'multiView': ['camera', 'upper'], 'comments': 'Some comment'},
        {'comments': 'Some comment - Processed by exrsplit', 'channels': {}},
    ),
])
def test__create_output_header(header, expected_header):
    assert exrsplit_main._create_output_header(header) == expected_header
