#!/bin/bash

#
# Setup RPi from fresh image of raspbrian.
# Usage: $init_rpi.sh 192.168.1.2
#
# - assumes; RPi is already attached to a network.
#            RPi IP address is known.
#            SSH is enabled (/boot/ssh file has been placed).
#
#

# Raspbrian defaults
DEFAULT_USER='pi'
DEFAULT_PASS='raspberry'

# Local file locations
PUB_KEY_PATH='/home/user1/.ssh/id_rsa.pub'

# Static IP to set rpi to
STATICIP='192.168.8.98'

#
# Test we can SSH into the RPi OK
#

# we want one arg, $1 to be an ip address
if [ $# -eq 1 ]; then
    # Remove any known_host for various hostnames and IPs
    ssh-keygen -R $1
    ssh-keygen -R $STATICIP
    ssh-keygen -R rpi
    ssh-keygen -R helga

    echo "Testing connection to RPi at $1:"
    
    # test connection
    cmd="sshpass -p $DEFAULT_PASS ssh $DEFAULT_USER@$1 -o StrictHostKeyChecking=no exit"
    echo -n -e "\tcheck we can ssh to $1 and login "
    $cmd
    # output result
    if [ $? -eq 0 ]; then
        echo "- OK"
        echo
    else
        echo "- FAILED"
        echo -e "\tFix it and re-run"
        exit -1
    fi
else
    echo "No IP address supplied."
    echo "Usage: init_rpi.sh <ip addr>"
    exit -1
fi

#
# Setup RPi Networking
#

# Set static IP on wlan0 - from file; ./files/dhcpcd.conf
echo "Configuring Networking:"
echo -e -n "\tcopying ./files/dhcpcd.conf to rpi "

# setup cmd and execute
cmd="sshpass -p $DEFAULT_PASS scp ./files/dhcpcd.conf $DEFAULT_USER@$1:/etc/"
$cmd
# output result
if [ $? -eq 0 ]; then
    echo "- OK"
else
    echo "- FAILED"
    echo "exiting"
    exit -1
fi

# write pub key to .ssh/authorized_keys
cmd="sshpass -p $DEFAULT_PASS ssh-copy-id -i $PUB_KEY_PATH $DEFAULT_USER@$1"
echo -n -e "\tadd public ssh key "
$cmd > /dev/null 2>&1
# output result
if [ $? -eq 0 ]; then
    echo "- OK"
else
    echo "- FAILED"
    exit -1
fi

# Restart to apply the static IP
echo -e -n "\trestarting rpi "
cmd="sshpass -p $DEFAULT_PASS ssh -q $DEFAULT_USER@$1 sudo reboot"
$cmd > /dev/null 2>&1
# We get cut off at reboot, return is 255.
if [ $? -eq 255 ]; then
    echo "- OK"
else
    echo "- FAILED"
    echo "exiting"
    exit -1
fi

# wait before re-connecting
echo -n -e "\twaiting for reboot "
sleep 60
echo "- OK"

# Test we can re-connect using keys (no password) on static IP
cmd="ssh -o StrictHostKeyChecking=no $DEFAULT_USER@$STATICIP exit"
echo -n -e "\tcheck we can ssh with keys only "
$cmd
# output result
if [ $? -eq 0 ]; then
    echo "- OK"
    echo
else
    echo "- FAILED to login"
    echo "Fix it and re-run"
    exit -1
fi
