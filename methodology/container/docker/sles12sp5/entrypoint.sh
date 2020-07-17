#!/bin/bash
/usr/app/vncserver.sh :1 -geometry 1280x1200 
#if [ -z "$SINGULARITY_CONTAINER" ] ; then
#    /sbin/rpcbind &
#    /usr/sbin/ypbind &
#    sleep 3
#    su - $USER --shell=/bin/bash 
#fi
/bin/bash
