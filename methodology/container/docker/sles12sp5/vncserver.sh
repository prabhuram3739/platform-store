#!/bin/bash -x

# trying to stop old session, if there's any
#/usr/intel/bin/vncserver -kill $1 && sleep 5

# delete old pid|log files
if test -n "$(find ~/.vnc/ -maxdepth 1 -regex ".*$HOSTNAME$1\.[pid\|log]..*" -print -quit)"; then
    echo "Cleaning up old vnc files"
    rm ~/.vnc/$HOSTNAME$1.{log,pid}*
fi

# delete old lock file
id=`echo $1 |cut -d: -f2`
find /tmp -maxdepth 1 -type f -name .X$id-lock -user $USER -exec rm -f {} \; 2> /dev/null
find /tmp/.X11-unix -maxdepth 1 -name X$id -user $USER -exec rm -f {} \; 2> /dev/null

#cp /usr/bin/xauth ~/
#printf "password\npassword\nn\n\n" | /usr/bin/vncpasswd

x=1
while [ $x -le 5 ]; do
        /usr/bin/vncserver $@
        exit_status=$?
        if [ $exit_status -eq 0 ]; then
                break
        elif [ $exit_status -eq 1 ]; then
            echo "Failed to run /usr/intel/bin, fall back to locally installed vncserver"
            vncserver $@
            break
        elif [ $exit_status -eq 81 ]; then
            echo ".Xauthority lock, sleeping then trying to unlock"
            sleep $(( RANDOM % (20 - 5 + 1 ) + 5 ))
            xauth -b q
        elif [ $exit_status -eq 90 ]; then
            echo "VNC session seem busy, terminating it.."
            ps ax|grep Xvnc |grep " :$id "
            ps ax|grep Xvnc |grep --color " :$id "|awk '{print $1}' |xargs kill -9
            sleep 5

        fi
        x=$(( $x + 1 ))
done
