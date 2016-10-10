#!/usr/bin/env bash
# Workaround Ubuntu 14.04 libIlmImf version (1.6.1), which doesn't support long
# header fields and long channel names (and breaks some tests)
set -e
mkdir -p ~/libopenexr /tmp/lib
pushd ~/libopenexr
wget https://launchpad.net/~bsundman/+archive/ubuntu/openexr/+files/libopenexr22_2.2.0-1bsundman1~trusty1_amd64.deb
wget https://launchpad.net/~bsundman/+archive/ubuntu/openexr/+files/libopenexr-dev_2.2.0-1bsundman1~trusty1_amd64.deb
wget https://launchpad.net/~bsundman/+archive/ubuntu/openexr/+files/libilmbase12_2.2.0-0bsundman1~trusty1_amd64.deb
wget https://launchpad.net/~bsundman/+archive/ubuntu/openexr/+files/libilmbase-dev_2.2.0-0bsundman1~trusty1_amd64.deb

ar xf libopenexr22_2.2.0-1bsundman1~trusty1_amd64.deb
tar xf data.tar.?z
ar xf libopenexr-dev_2.2.0-1bsundman1~trusty1_amd64.deb
tar xf data.tar.?z
ar xf libilmbase12_2.2.0-0bsundman1~trusty1_amd64.deb
tar xf data.tar.?z
ar xf libilmbase-dev_2.2.0-0bsundman1~trusty1_amd64.deb
tar xf data.tar.?z

mv -f usr/lib/x86_64-linux-gnu/* /tmp/lib
mv -f usr/include /tmp

popd
rm -rf ~/libopenexr
