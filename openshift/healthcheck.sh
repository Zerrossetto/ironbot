#!/bin/sh

file_name=${HEARTBEAT_FILE-'/tmp/ironbot-heartbeat'}

if [[ -f ${file_name} ]]; then

    # getting last modified date from the hearbeat file
    heartbeat=$(stat -c %Y ${file_name} 2>/dev/null)
    if [ -z "$heartbeat" ]; then
        # fix for BSD systems
        heartbeat=$(stat -f %m ${file_name} 2>/dev/null)
    fi

    if [ -z "$heartbeat" ]; then
        logger -s "Unable to retrieve last heartbeat time"
        exit_code=2
    else
        limit=${1-600}
        diff=$(( $(date +%s) - heartbeat ))
        if [ "$diff" -gt "$limit" ]; then
            logger -s "Heartbeat token expired (with $diff > $limit seconds)"
            exit_code=1
        else
            # Everything's fine
            exit_code=0
        fi
    fi
else
    logger -s "Heartbeat file \"$file_name\" not found"
    exit_code=1
fi

exit ${exit_code}
