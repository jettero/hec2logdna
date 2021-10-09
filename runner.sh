#!/bin/bash

if [ -z "$LOGDNA_TOKEN" ]
then echo "set the LOGDNA_TOKEN"; exit 1
fi

if [ -z "$HEC2LDNA_PORT" ]
then echo "set the HEC2LDNA_PORT"; exit 1
fi

[ -n "$HEC2LDNA_CERTFILE" ] || unset HEC2LDNA_KEYFILE
[ -n "$HEC2LDNA_KEYFILE"  ] || unset HEC2LDNA_CERTFILE

while true
do ( set -x;
    sudo LOGDNA_TOKEN=$LOGDNA_TOKEN gunicorn --bind=0.0.0.0:$HEC2LDNA_PORT --workers=3 \
    ${HEC2LDNA_CERTFILE:+--certfile} $HEC2LDNA_CERTFILE \
    ${HEC2LDNA_KEYFILE:+--keyfile} $HEC2LDNA_KEYFILE \
    --user $USER --group www-data --log-file=- --reload \
    hubble:app )

echo; echo sleeping
sleep 2
done
