from cmdargs import CmdArgs
import exrsplit.__main__ as exrsplit_main
import os
import pytest
import sys

# This file contains tests that are run against the openexr-images repository
# (https://github.com/openexr/openexr-images.git).

openexr_images_submodule = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'openexr-images')
has_submodule = os.path.isfile(os.path.join(openexr_images_submodule, 'LICENSE'))
if pytest.config.getvalue('--skip-slow'):
    pytestmark = pytest.mark.skip('--skip-slow specified')
elif not has_submodule:
    pytestmark = pytest.mark.skip('openexr-images submodule unavailable')


def image_path(dirpath, filename):
    if sys.version_info >= (3, 0) and dirpath.endswith('ScanLines') and filename == 'Blobbies.exr':
        return pytest.mark.skip('pythonopenexr crash in Python 3')  # investigate this segfault
    return os.path.join(dirpath, filename)

if has_submodule:
    openexr_images = []
    for dirpath, _, filenames in os.walk(openexr_images_submodule):
        openexr_images.extend([image_path(dirpath, x) for x in filenames if x.endswith('.exr')])


@pytest.mark.parametrize('image', openexr_images)
def test_split_image(image):
    exrsplit_main.main(CmdArgs(png=False, split_channels=False, merge=False, image=[image]))
