#!/bin/bash

# ====================================================================================================================
#
# Script Name:      init_rpi.sh
#
# Author:           James Park, Linux Networks Ltd.
# Date:             12/06/18
#
# Description:      The following script performs basic network configuration of a linux host over ssh.
#                   Specifically it;
#                       - Tests it can make an ssh connection to the host with the default credentials supplied.
#                       - Copies a dhcp configuration file (providing a static ip address) to the host.
#                       - Adds a public key to .ssh/authorized_keys on the host.
#                       - Reboots the host.
#                       - Tests it can re-connect using the static ip address and the ssh key.
#
#                   For any of those things to happen, it is assumed that;
#                       - The host is already attached to a network.
#                       - The current hostname or IP address is known.
#                       - SSH is enabled, valid credentials are known.
#
# Run Information:  Expects a single argument, hostname or IP address. e.g ./init_rpi.sh <host1>
#
# Error Log:        None. Console output only.
#
# ====================================================================================================================

# Host is a Pi.
# Raspbrian defaults.
DEFAULT_USER='pi'
DEFAULT_PASS='raspberry'

# Local file locations.
PUB_KEY_PATH='~/.ssh/id_rsa.pub'
DHCP_CONF_PATH='./conf/dhcpcd.conf'

# Static IP to set on host.
# This same address must also be the static address within dhcpcd.conf.
# TODO: Remove this cross-file address duplication.
STATICIP='192.168.8.98'

#
# Test we can SSH into the host OK.
#

# We want one arg, $1 to be an IP address.
if [[ $# -eq 1 ]]; then
    # Remove any ssh known_host for various hostnames and IPs.
    ssh-keygen -R $1
    ssh-keygen -R ${STATICIP}
    ssh-keygen -R rpi
    ssh-keygen -R helga

    echo "Testing connection to host at $1:"
    
    # Test connection.
    cmd="sshpass -p ${DEFAULT_PASS} ssh ${DEFAULT_USER}@$1 -o StrictHostKeyChecking=no exit"
    echo -n -e "\tcheck we can ssh to $1 and login "
    ${cmd}
    # Output result.
    if [[ $? -eq 0 ]]; then
        echo "- OK."
        echo
    else
        echo "- FAILED."
        echo -e "\tFix it and re-run."
        exit -1
    fi
else
    echo "No IP address supplied."
    echo "Usage: $0 <ip addr>"
    exit -1
fi

#
# Setup host networking.
#

# Set static IP address - from file; ./conf/dhcpcd.conf.
echo "Configuring Networking:"
echo -e -n "\tcopying ${DHCP_CONF_PATH} to host "

# Build command and execute.
cmd="sshpass -p ${DEFAULT_PASS} scp ${DHCP_CONF_PATH} ${DEFAULT_USER}@$1:/etc/"
${cmd}
# Output result.
if [[ $? -eq 0 ]]; then
    echo "- OK."
else
    echo "- FAILED."
    echo "exiting."
    exit -1
fi

# Write public key to .ssh/authorized_keys.
cmd="sshpass -p ${DEFAULT_PASS} ssh-copy-id -i ${PUB_KEY_PATH} ${DEFAULT_USER}@$1"
echo -n -e "\tadd public ssh key "
${cmd} > /dev/null 2>&1
# Output result.
if [[ $? -eq 0 ]]; then
    echo "- OK."
else
    echo "- FAILED."
    exit -1
fi

#
# Apply and test the changes.
#

# Reboot host.
echo -e -n "\trestarting host "
cmd="sshpass -p ${DEFAULT_PASS} ssh -q ${DEFAULT_USER}@$1 sudo reboot"
${cmd} > /dev/null 2>&1
# We get cut off at reboot, return is 255.
if [[ $? -eq 255 ]]; then
    echo "- OK."
else
    echo "- FAILED."
    echo "exiting."
    exit -1
fi

# Wait before re-connecting.
echo -n -e "\twaiting for reboot "
sleep 60
echo "- OK."

# Test we can re-connect using keys (no password) on the static IP address just set.
cmd="ssh -o StrictHostKeyChecking=no ${DEFAULT_USER}@${STATICIP} exit"
echo -n -e "\tcheck we can ssh with keys only "
${cmd}
# Output result.
if [[ $? -eq 0 ]]; then
    echo "- OK."
    echo
else
    echo "- FAILED to login."
    echo "Fix it and re-run."
    exit -1
fi
