#!/usr/bin/env bash

if [[ -f ${HEARTBEAT_FILE} ]]; then

    heartbeat=$(stat -c %Y ${HEARTBEAT_FILE} 2>/dev/null)
    if [ -z "$heartbeat" ]; then
        # fix for BSD systems
        heartbeat=$(stat -f %m ${HEARTBEAT_FILE} 2>/dev/null)
    fi
    if [ -z "$heartbeat" ]; then
        logger -s "Unable to retrieve last heartbeat time"
        exit 2
    fi

    if [[ $(( $(date +%s) - heartbeat )) > $1 ]]; then
        logger -s "Heartbeat token expired (current limit is $1 seconds)"
        exit 1
    fi
else
    logger -s "Heartbeat file \"$HEARTBEAT_FILE\" not found"
    exit 1
fi

exit 0