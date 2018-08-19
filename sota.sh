#!/bin/bash

if [ -n "$DEBUG" ]; then
    PS4=':${LINENO}+'
    set -x
fi

SCRIPT_FILE="$0"
SCRIPT_NAME="$(basename "$SCRIPT_FILE")"
SCRIPT_PATH="$(dirname "$SCRIPT_FILE")"
if [ -L "$0" ]; then
    REAL_FILE="$(readlink "$0")"
    REAL_NAME="$(basename "$REAL_FILE")"
    REAL_PATH="$(dirname "$REAL_FILE")"
fi

SPACES=" |'"
BINDIR="$SCRIPT_PATH/bin"
LIBDIR="$SCRIPT_PATH/lib"
PROGRAM="$BINDIR/sota"
PYTHON=`which python2`
ARGS=()
for ARG in "$@"; do
    case $ARG in
        --pdb)
        PROGRAM="$PYTHON -m pdb $SCRIPT_PATH/target.py"
        ;;
        --py)
        PROGRAM="$PYTHON $SCRIPT_PATH/target.py"
        ;;
        *)
        if [[ $ARG =~ $SPACES ]]; then
            ARG="'$ARG'"
        fi
        ARGS+=("${ARG}")
        ;;
    esac
done
CMD="LD_LIBRARY_PATH=lib:$LD_LIBRARY_PATH ${PROGRAM} ${ARGS[@]}"
eval "$CMD"
exit $?
