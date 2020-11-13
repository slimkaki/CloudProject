#!/bin/bash
cd /home/ubuntu/
sudo apt update
sudo apt install postgresql postgresql-contrib -y
sudo su - postgres
psql -U postgres -c "CREATE USER cloud WITH PASSWORD 'cloud';"
createdb -O cloud tasks
sed -e "s/#listen_addresses = 'localhost'.*$/listen_addresses = '*'/g" /etc/postgresql/10/main/postgresql.conf > /etc/postgresql/10/main/aa.conf
cat /etc/postgresql/10/main/aa.conf > /etc/postgresql/10/main/postgresql.conf
rm /etc/postgresql/10/main/aa.conf
echo -e "host\t all\t all\t 0.0.0.0/0\t trust" >> /etc/postgresql/10/main/pg_hba.conf
exit
echo "sai do postgres, vou liberar o firewall" > /home/ubuntu/fire.txt
sudo ufw allow 5432/tcp
echo "tudo liberado" > /home/ubuntu/done.txt
sudo systemctl restart postgresql