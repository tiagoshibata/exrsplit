import exrsplit.__main__ as exrsplit_main
from mock import ANY, call, patch, MagicMock
import pytest
from cmdargs import CmdArgs


@pytest.mark.parametrize('flags', [
    (CmdArgs(png=False, split_channels=False, merge=True, image=['a', 'b'])),
    (CmdArgs(png=False, split_channels=True, merge=True, image=['a', 'b', 'c'])),
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


@patch('OpenEXR.OutputFile')
@patch('exrsplit.__main__._open_inputfile')
def test_split_exr_layers(mock___open_inputfile, mock_OpenEXR_OutputFile):
    mock_exr = MagicMock()
    mock_exr.header = lambda: {'channels': {'R': {}, 'G': {}, 'car.R': {}}}
    mock___open_inputfile.side_effect = lambda x: mock_exr
    args = CmdArgs(png=False, split_channels=False, merge=False, image=['test.exr'])
    exrsplit_main.split_exr(args)

    mock___open_inputfile.assert_called_once_with('test.exr')
    mock_OpenEXR_OutputFile.assert_has_calls([
        call('car.exr', {
            'channels': {'R': {}},
            'comments': 'Processed by exrsplit',
        }),
        call().writePixels(ANY),
        call().close(),
        call('default_layer.exr', {
            'channels': {'R': {}, 'G': {}},
            'comments': 'Processed by exrsplit',
        }),
        call().writePixels(ANY),
        call().close(),
    ])
