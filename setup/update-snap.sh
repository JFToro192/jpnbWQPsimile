#!/bin/bash

/usr/local/snap/bin/snap --nosplash --nogui --modules --refresh --update org.esa.s3tbx.s3tbx.landsat.reader org.esa.s3tbx.s3tbx.c2rcc 2>&1 | while read -r line; do
    echo "$line"
    [ "$line" = "updates=0" ] && sleep 2 && pkill -TERM -f "snap/jre/bin/java"
done