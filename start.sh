#!/bin/bash
pip3 install -r requirements.txt
cd config/
python3 routine.py
chmod 400 ./credentials/botorafak.pem 