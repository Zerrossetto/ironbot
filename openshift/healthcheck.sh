#!/usr/bin/env bash

if [[ -f ${HEARTBEAT_FILE} ]]; then

    # getting last modified date from the hearbeat file
    heartbeat=$(stat -c %Y ${HEARTBEAT_FILE} 2>/dev/null)
    if [ -z "$heartbeat" ]; then
        # fix for BSD systems
        heartbeat=$(stat -f %m ${HEARTBEAT_FILE} 2>/dev/null)
    fi

    if [ -z "$heartbeat" ]; then
        logger -s "Unable to retrieve last heartbeat time"
        exit_code=2
    elif [[ $(( $(date +%s) - heartbeat )) > $1 ]]; then
        logger -s "Heartbeat token expired (current limit is $1 seconds)"
        exit_code=1
    else
        exit_code=0
    fi
else
    logger -s "Heartbeat file \"$HEARTBEAT_FILE\" not found"
    exit_code=1
fi

exit ${exit_code}
