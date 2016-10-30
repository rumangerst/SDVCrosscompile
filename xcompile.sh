#!/bin/bash

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
 
$SCRIPTDIR/xcompile.py --lib-windows $SCRIPTDIR/lib-windows --lib-linux $SCRIPTDIR/lib-linux --lib-mac $SCRIPTDIR/lib-mac "$@"
