# !/bin/bash
# Install Chrome WebDriver on a Debian-based system
sudo apt update -y
sudo apt upgrade -y
mkdir -p .drivers
cd .drivers
LOCAL_DEB="./chrome.deb"
wget -q -O $LOCAL_DEB https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install -y $LOCAL_DEB
rm $LOCAL_DEB
cd -
