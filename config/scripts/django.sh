#!/bin/bash
cd /home/ubuntu
sudo apt update
sudo apt install python3-pip -y
git clone https://github.com/raulikeda/tasks.git
echo "clonei" > clone.txt
cd tasks/portfolio/
sed -i "s/'HOST': 'node1',/'HOST': '172.31.25.125',/g" settings.py
cd ..
chmod +x install.sh
./install.sh
echo "instalei tudo do git" > fim.txt