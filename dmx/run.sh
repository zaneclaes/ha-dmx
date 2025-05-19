#!/bin/bash
set -ueo pipefail

sudo chgrp dmxuser /dev/ttyUSB0
sudo chmod 666 /dev/ttyUSB0

su - dmxuser -c 'HOME=/home/dmxuser start.sh'