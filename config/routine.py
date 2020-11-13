import boto3, time, json, paramiko, os
from CloudConfig import Cloud

def main():
    with open("./credentials/credentials.json", "r") as file:
        secrets = json.load(file)
    
    myCloudOhio = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                    secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                    region="us-east-2")

    chave = "botorafak"
    sg_name = "sec_kaki_OHIO"
    myCloudOhio.loadRSA(chave)
    # Cria grupo de seguranca: portas 22 e 5432 liberadas
    myCloudOhio.createSecurityGroup(sg_name, [22, 80, 443, 5432, 8080])

    # Cria instância em OHIO
    myTags = {'ResourceType': 'instance','Tags': [{'Key': 'rafaPostgres','Value': 'Postgres'},]}
    inst1 = myCloudOhio.createInstance('t2.micro', myTags, sg_name, chave, open("./scripts/postgres.sh").read(), myCloudOhio.ami_ubuntu18_ohio)

    # Executa script postgresql
    print("sleeping for 120 seconds")
    t0 = time.time()
    while (time.time()-t0 < 120):
        print("> " + str(int(120-(time.time()-t0))) + " segundos ", end="\r")
    print("just woke up!")

    ip_postgres = myCloudOhio.getIP(inst1[0], "PrivateIpAddress")

    editShellScript("./scripts/django.sh", ip_postgres)
    myTags = {'ResourceType': 'instance','Tags': [{'Key': 'rafaDjango','Value': 'Django'},]}
    inst2 = myCloudOhio.createInstance('t2.micro', myTags, sg_name, chave, open("./scripts/django.sh").read(), myCloudOhio.ami_ubuntu18_ohio)
    print("\nInstancia Django:")
    myCloudOhio.getIP(inst2[0])

def editShellScript(path, ip_postgres):
    file_read = open(path, "rt")
    data = file_read.read()
    data = data.replace("<replace me with ip>", ip_postgres)
    file_read.close()
    file_write = open(path, "wt")
    file_write.write(data)
    file_write.close()
    print(".sh já está pronto!")

if __name__ == '__main__':
    main()