#!/bin/bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo su - postgres
createuser -s cloud -W