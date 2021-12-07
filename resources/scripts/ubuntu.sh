#!/bin/bash
#
# GitHub Repository: https://github.com/Thegreatfoxxgoddess/Paimon

echo "Installation script for paimon by fnixdev"

if [ $(id -u) = 0 ]; then
   echo "This script should not run as root or sudo. Run normally with./ubuntu.sh. Logging out..."
   exit 1
fi

# Installing dependencies
echo "Installing dependencies.."
if [ ! -n "`which sudo`" ]; then
  apt-get update && apt-get install sudo -y
fi
sudo apt-get update -y
sudo apt-get install tree -y
sudo apt-get install wget2 -y
sudo apt-get install p7zip-full -y
sudo apt-get install jq -y
sudo apt-get install ffmpeg -y
sudo apt-get install wget -y
sudo apt-get install git -y
sudo wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb -y
sudo rm google-chrome-stable_current_amd64.deb
echo "Installing Python3.9..."
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.9 -y
sudo apt install neofetch -y

echo "Cloning repository."
cd ~
sudo git clone https://github.com/Thegreatfoxxgoddess/Paimon.git
cd Paimon

echo "Installing Paimon requirements."
sudo pip install -r requirements.txt
sudo pip3 install -r requirements.txt
sudo cp config.env.sample config.env
echo "Configuring Screen ..."

sudo apt install screen -y
echo "Installation completed."