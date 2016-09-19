"""Verify EXR file and dump some of its header."""
import OpenEXR


def _parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true', help='Display all header information')
    parser.add_argument('target', nargs='+', help='Input image')
    return parser.parse_args()

args = _parse_args()
for exr_filename in args.target:
    print('{}:'.format(exr_filename))
    if not OpenEXR.isOpenExrFile(exr_filename):
        print("Invalid EXR image")
        continue

    exr_file = OpenEXR.InputFile(exr_filename)
    try:
        if not exr_file.isComplete:
            print("Exr file isn't complete (corrupted or some program is still writing to the file?)")
            continue

        exr_header = exr_file.header()
        if args.all:
            for key, value in exr_header.items():
                print('{} - {}'.format(key, value))

        print('Channels:')
        for channel_name, channel_type in exr_header['channels'].items():
            print('{} - {}'.format(channel_name, channel_type))

        if 'multiView' in exr_header:
            print('multiView: {}'.format(', '.join(exr_header['multiView'])))
    finally:
        exr_file.close()
