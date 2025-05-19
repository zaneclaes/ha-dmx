#!/bin/bash
set -ueo pipefail

# chgrp dmxuser /dev/ttyUSB0
chmod 666 /dev/ttyUSB0

su - dmxuser -c 'HOME=/home/dmxuser start.sh'