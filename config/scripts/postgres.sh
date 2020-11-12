#!/bin/bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo su - postgres
createuser -s cloud -W # (add senha cloud)
createdb -O cloud tasks
sed -e "s/#listen_addresses = 'localhost'.*$/listen_addresses = '*'/g" /etc/postgresql/10/main/postgresql.conf > /etc/postgresql/10/main/aa.conf
cat /etc/postgresql/10/main/aa.conf > /etc/postgresql/10/main/postgresql.conf
rm /etc/postgresql/10/main/aa.conf
echo -e "host\t all\t all\t 0.0.0.0/0\t trust" >> /etc/postgresql/10/main/pg_hba.conf