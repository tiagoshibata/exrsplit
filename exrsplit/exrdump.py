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

# Verify EXR file and dump some of its header

import OpenEXR
import sys

if len(sys.argv) == 1:
    print('Usage: exrdump [-a] file.exr [file2.exr ...]\n'
          '\t-a\t\tDisplay all header information')

display_header = sys.argv[1] == '-a'
if display_header:
    exr_files = sys.argv[2:]
else:
    exr_files = sys.argv[1:]

for exr_filename in exr_files:
    print('%s:' % (exr_filename))
    if not OpenEXR.isOpenExrFile(exr_filename):
        print("Invalid EXR image")
        exit(1)

    exr_file = OpenEXR.InputFile(exr_filename)
    if not exr_file.isComplete:
        print("Exr file isn't complete (corrupted or some program is still writing to the file?)")
        exit(1)

    exr_header = exr_file.header()

    if display_header:
        for key, value in exr_header.items():
            print('%s - %s' % (key, value))

    print('Channels:')

    for channel_name, channel_type in exr_header['channels'].items():
        print('%s - %s' % (channel_name, channel_type))

    if 'multiView' in exr_header:
        print('multiView data:')
        print(exr_header['multiView'])
    else:
        print('No multiView data')

    exr_file.close()
