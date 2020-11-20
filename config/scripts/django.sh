#!/bin/bash
cd /home/ubuntu
sudo apt update
sudo apt install python3-pip -y
git clone https://github.com/slimkaki/tasks.git
echo "clonei" > clone.txt
cd tasks/portfolio/
sed -i "s/'HOST': 'node1',/'HOST': '<replace me with ip>',/g" settings.py
cd ..
echo "sudo reboot" >> install.sh
chmod +x install.sh
./install.sh
echo "instalei tudo do git" > fim.txt