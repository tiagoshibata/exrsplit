from __future__ import print_function
import copy
import exrsplit
import OpenEXR
import sys


def _parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--png', action='store_true', help='Convert output images to PNG')
    parser.add_argument('-m', '--merge', action='store_true', help='Merge multiple OpenEXR images')
    parser.add_argument('--view', action='append', help='Treat given prefix as a view instead of a layer')
    parser.add_argument('image', nargs='+', help='Input images (last argument used as output if merging)')
    return parser.parse_args()


def _open_inputfile(filename):
    if not OpenEXR.isOpenExrFile(filename):
        print("Failed reading image. File can't be opened or is not an OpenEXR image")
        raise SystemExit(1)
    exr_file = OpenEXR.InputFile(filename)
    if not exr_file.isComplete():
        print("File is incomplete (corrupted or still being written)")
        exr_file.close()
        raise SystemExit(1)
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


def main(args):
    if args.merge:
        if len(args.image) < 3:
            print('Error: --merge required at least two inputs and one output image', file=sys.stderr)
            raise SystemExit(1)
        raise NotImplementedError
    else:
        for inputfile in args.image:
            exr = _open_inputfile(inputfile)
            header = exr.header()
            channels = [exrsplit.EXRChannel(header, layer) for layer in header['channels']]
            grouped_channels = exrsplit.group_color_channels(channels)
            for layer_i, layer in enumerate(grouped_channels):
                target_file = '{}.exr'.format(exrsplit.output_file_name(layer[0]))
                print('{}/{} - Saving {} channels to {}'.format(layer_i + 1, len(grouped_channels),
                                                                len(layer), target_file))
                out_header = _create_output_header(header)
                channel_data = {}
                for channel in layer:
                    if channel.channel_type == 'DATA':
                        # Copy pixel format
                        out_header['channels'] = {x: header['channels'][channel.channel] for x in ('R', 'G', 'B')}
                        channel_data = {x: exr.channel(channel.channel) for x in ('R', 'G', 'B')}
                    else:
                        out_header['channels'][channel.channel] = header['channels'][channel.channel]
                        channel_data[channel.channel] = exr.channel(channel.channel)
                output = OpenEXR.OutputFile(target_file, out_header)
                output.writePixels(channel_data)

if __name__ == '__main__':
    main(_parse_args())
