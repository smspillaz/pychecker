#!/bin/sh
# -*- Mode: shell-script; -*-
#
# cvs-loginfo.sh - script to mail users a msg indicating a check-in has occured
#		   and update a change log file
#
# Copyright (c) 2000 Eric C. Newton <ecn@fault-tolerant.org>
#
# This file is part of Recall, a fault-tolerant, replicated storage
# server.
#

# Programs
DIRNAME=dirname
CAT=cat
CUT=cut
DATE=date
EGREP=egrep
MAIL=Mail
TEE=tee

SEPARATOR="------------------------------------"
umask 002

BASE_DIR=`$DIRNAME $0`
MAIL_USERS_FILE=mail_users
MAIL_USERS=$BASE_DIR/$MAIL_USERS_FILE
CHANGE_LOG=$BASE_DIR/ChangeLog

# Checkout a readable version of the mail users file
cd $BASE_DIR
co -u $MAIL_USERS_FILE,v > /dev/null 2>&1
co -u cvs-taginfo.sh > /dev/null 2>&1
chmod ug+w $CHANGE_LOG

# Verify the readable version exists
if [ ! -r $MAIL_USERS ]; then
    echo "$0: unable to read file: $MAIL_USERS, exiting"
    exit 10
fi

MAIL_USERS=`cat $MAIL_USERS`

# FIXME: really oughta check the parameters are all there

USER="$1"
FILES="$2"
OLD_VERSION="$3"
NEW_VERSION="$4"

function first
{
    echo $1
}
function rest
{
    shift
    echo $*
}

DIR=`first $FILES`
FILES=`rest $FILES`
MODULE=`echo $DIR | $CUT -d/ -f1`

( $DATE ; echo ; echo "Change made by $USER" ; \
	echo ; $EGREP -v "^In directory " ; echo $SEPARATOR ) | \
 $TEE --append $CHANGE_LOG | $MAIL -s "CVS Change for $MODULE" $MAIL_USERS

exit 0
