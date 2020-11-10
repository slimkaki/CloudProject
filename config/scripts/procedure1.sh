#!/bin/bash
sudo apt-get update && upgrade
sudo apt-get -y install python3-pip
sudo apt update
sudo apt install mysql-server -y
sudo mysql_secure_installation
pip3 install fastapi uvicorn uuid mysql
git clone http://github.com/slimkaki/megadadosAPS1
cd megadadosAPS1/
export PYTHONPATH=$(pwd)/tasklist:$PYTHONPATH
uvicorn 