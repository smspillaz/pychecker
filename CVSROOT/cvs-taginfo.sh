#!/bin/sh
# -*- Mode: shell-script; -*-
#
# cvs-taginfo.sh - script run when a tag is made in CVS
#		   if it's a new tag, check-in the change log
#
# Copyright (c) 2000 Eric C. Newton <ecn@fault-tolerant.org>
#
# This file is part of Recall, a fault-tolerant, replicated storage
# server.
#

# Programs
DIRNAME=dirname
MV=mv

umask 002

BASE_DIR=`$DIRNAME $0`
CHANGE_LOG=ChangeLog
TMP=${CHANGE_LOG}.tmp

# FIXME: really oughta check the parameters are all there

TAG="$1"
OPERATION="$2"
MODULE="$3"
FILE_REVS="$4"

# We only do work when a tag is added
cd $BASE_DIR
if [ "$OPERATION" != "add" -o ! -r "$CHANGE_LOG" ]; then
    exit 0
fi

# The ChangeLog isn't checked out, so:
#   move ChangeLog to tmp, check-out, move tmp to ChangeLog, check-in
mv $CHANGE_LOG $TMP
co -l $CHANGE_LOG
mv $TMP $CHANGE_LOG
ci -u $CHANGE_LOG
chmod ug+w $CHANGE_LOG

exit 0
