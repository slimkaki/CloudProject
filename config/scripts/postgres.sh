#!/bin/bash
cd /home/ubuntu/
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo -u postgres psql -c "CREATE USER cloud WITH PASSWORD 'cloud';"
sudo -u postgres createdb -O cloud tasks 
sudo -u postgres sed -i "s/#listen_addresses = 'localhost'.*$/listen_addresses = '*'/g" /etc/postgresql/10/main/postgresql.conf
echo -e "host\t all\t all\t 0.0.0.0/0\t trust" | sudo -u postgres tee -a /etc/postgresql/10/main/pg_hba.conf
echo "sai do postgres, vou liberar o firewall" > /home/ubuntu/fire.txt
sudo ufw allow 5432/tcp
echo "tudo liberado" > /home/ubuntu/done.txt
sudo systemctl restart postgresql