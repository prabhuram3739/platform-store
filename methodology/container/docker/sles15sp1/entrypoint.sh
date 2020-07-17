#!/bin/bash
/sbin/rpcbind &
/usr/sbin/ypbind -debug &
/usr/bin/ssh-keygen -A
/usr/sbin/sshd -D &
