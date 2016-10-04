from cmdargs import CmdArgs
import exrsplit.__main__ as exrsplit_main
import os
import pytest

# This file contains tests that are run against the openexr-images repository
# (https://github.com/openexr/openexr-images.git).

openexr_images_submodule = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'openexr-images')
has_submodule = os.path.isfile(os.path.join(openexr_images_submodule, 'LICENSE'))
uses_openexr_images = pytest.mark.skipif(not has_submodule or pytest.config.getvalue('--skip-slow'),
                                         reason='openexr-images submodule unavailable or --skip-slow specified')
if has_submodule:
    openexr_images = []
    for dirpath, _, filenames in os.walk(openexr_images_submodule):
        openexr_images.extend([os.path.join(dirpath, x) for x in filenames if x.endswith('.exr')])


@uses_openexr_images
@pytest.mark.parametrize('image', openexr_images)
def test_split_image(image):
    exrsplit_main.main(CmdArgs(png=False, split_channels=False, merge=False, image=[image]))
