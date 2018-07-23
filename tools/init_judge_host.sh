#!/bin/bash

# Author: Yuan
# RUN THIS SCRIPT AS ROOT
# DO NOT RUN THIS SCRIPT IN FOLDER WHICH OWNED BY ROOT

apt-get update
apt-get -y install build-essential
apt-get -y install git
apt-get -y install curl
apt-get -y install htop
apt-get -y install zsh

# Python
apt-get -y install rsync
apt-get -y install python3-pip python3-dev

# Python third lib
pip3 install pika

# Add user judge. group: sudo.
useradd -g sudo -s /bin/zsh -m judge
echo "Modifying password of judge, input new password."
passwd judge

# Install oh-my-zsh.
sudo -H -u judge sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"

