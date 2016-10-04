from __future__ import print_function
import copy
import exrsplit
import OpenEXR
import os
import sys


def _parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--png', action='store_true', help='Convert output images to PNG')
    parser.add_argument('-m', '--merge', action='store_true', help='Merge multiple OpenEXR images')
    parser.add_argument('-s', '--split-channels', action='store_true', help='Create a file for each channel instead ' +
                        'of per layer. Data channels are saved as grayscale images.')
    parser.add_argument('--view', action='append',
                        help='Treat given prefix as a view instead of a layer. ' +
                        'First view is treated as the default view.')
    parser.add_argument('image', nargs='+', help='Input images (if merging, the header data is taken' +
                        'from first argument and last argument is used as output)')
    return parser.parse_args()


def _open_inputfile(filename):
    if not OpenEXR.isOpenExrFile(filename):
        print("Failed reading image. File can't be opened or is not an OpenEXR image.")
        raise SystemExit(1)
    exr_file = OpenEXR.InputFile(filename)
    if not exr_file.isComplete():
        print("WARNING: File seems incomplete (corrupted or still being written).")
    return exr_file


def _create_output_header(header):
    """Create the header of the output file from the input file.

    Keep most metadata, but remove view, multiView and channel information and add comment.
    """
    header = copy.deepcopy(header)
    header['channels'] = {}
    header.pop('view', None)
    header.pop('multiView', None)
    comment = 'Processed by exrsplit'
    prev_comment = header.setdefault('comments', comment)
    if prev_comment is not None and comment not in prev_comment:
        header['comments'] = '{} - {}'.format(prev_comment, comment)
    return header


def merge_exr(args):
    if len(args.image) < 3:
        print('Error: --merge requires at least two inputs and one output image.', file=sys.stderr)
        raise SystemExit(1)

    exr = _open_inputfile(args.image[0])
    output_header = _create_output_header(exr.header())
    exr.close()
    views = args.view or []
    if len(views) > 1:
        print('Using views {}'.format(', '.join(views)))
        output_header['multiView'] = views
    elif len(views) == 1:
        print('Using view {}'.format(views[0]))
        output_header['view'] = views[0]
        views = []

    channel_data = {}
    for i, inputfile in enumerate(args.image[:-1]):
        print('{}/{} - Merging {}'.format(i + 1, len(args.image) - 1, inputfile))
        exr = _open_inputfile(inputfile)
        header = exr.header()
        layers = os.path.basename(inputfile).split('.')[:-1]  # Split components and remove extension
        if layers[0] == 'default_layer':
            layers = layers[1:]
        if views:
            if layers[0] in views:
                if layers[0] == views[0]:
                    layers = layers[1:]
            else:
                print('{} first component is {}, which is not a valid view.'.format(inputfile, layers[0]))
                print('Putting in default view {}.'.format(views[0]))
        layer = '.'.join(layers)
        for channel in header['channels']:
            layer_fullname = layer and '{}.{}'.format(layer, channel) or channel
            channel_data[layer_fullname] = exr.channel(channel)
            output_header['channels'][layer_fullname] = header['channels'][channel]

    output = OpenEXR.OutputFile(args.image[-1], output_header)
    try:
        output.writePixels(channel_data)
    finally:
        output.close()


def split_exr(args):
    for inputfile in args.image:
        exr = _open_inputfile(inputfile)
        try:
            header = exr.header()
            channels = [exrsplit.EXRChannel(header, layer) for layer in header['channels']]
            if args.split_channels:
                grouped_channels = [[x] for x in channels]
            else:
                grouped_channels = exrsplit.group_channels(channels)
            for layer_i, layer in enumerate(grouped_channels):
                if args.split_channels:
                    target_file = '{}.{}.exr'.format(exrsplit.output_file_name(layer[0]), layer[0].channel)
                else:
                    target_file = '{}.exr'.format(exrsplit.output_file_name(layer[0]))
                print('{}/{} - Saving {} channels to {}'.format(layer_i + 1, len(grouped_channels),
                                                                len(layer), target_file))
                out_header = _create_output_header(header)
                channel_data = {}
                for channel in layer:
                    if channel.channel_type == 'DATA' and args.split_channels:
                        # Copy pixel format
                        out_header['channels'] = {x: header['channels'][channel.fullname] for x in ('R', 'G', 'B')}
                        channel_data = {x: exr.channel(channel.fullname) for x in ('R', 'G', 'B')}
                    else:
                        out_header['channels'][channel.channel] = header['channels'][channel.fullname]
                        channel_data[channel.channel] = exr.channel(channel.fullname)
                output = OpenEXR.OutputFile(target_file, out_header)
                output.writePixels(channel_data)
                output.close()
        finally:
            exr.close()


def main(args):
    if args.merge:
        merge_exr(args)
    else:
        split_exr(args)

if __name__ == '__main__':
    main(_parse_args())
