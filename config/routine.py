import boto3, time, json, paramiko, os
from CloudConfig import Cloud

def teste_vital():
    # Carrega as credenciais
    with open("./credentials/credentials.json", "r") as file:
        secrets = json.load(file)

    # Inicia sessão em OHIO
    myCloudOhio = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                    secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                    region="us-east-2")

    # Inicia sessão em NORTH VIRGINIA
    myCloudNV = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                    secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                    region="us-east-1")

    # Salvando alguns nomes em variáveis
    chave_ohio = "boto_rafa_ohio"  # Chave RSA OHIO 
    chave_nv = "boto_rafa_nv"      # Chave RSA NORTH VIRGINIA 

    sg_ohio = "sec_rafa_OHIO"      # Grupo de segurança de OHIO
    sg_nv = "sec_rafa_NV"          # Grupo de segurança de NORTH VIRGINIA

    # Cria as chaves de acesso
    myCloudOhio.createRSA(chave_ohio)
    myCloudNV.createRSA(chave_nv)
    
    # Cria os grupos de segurança
    myCloudOhio.createSecurityGroup(sg_ohio, [22, 5432]) # Postgresql Server
    myCloudNV.createSecurityGroup(sg_nv, [22, 8080]) # Django server

    # Cria as tags das instâncias
    myTagsPostGres = {'ResourceType': 'instance','Tags': [{'Key': 'rafaPostgres','Value': 'Postgres'},]}
    myTagsDjango = {'ResourceType': 'instance','Tags': [{'Key': 'rafaDjango','Value': 'Django'},]}

    # Cria a primeira instância do Postgres em Ohio
    postgres = myCloudOhio.createInstance('t2.micro', myTagsPostGres, sg_ohio, chave_ohio, open("./scripts/postgres.sh").read(), myCloudOhio.ami_ubuntu18_ohio)
    
    # Guarda o IP público do Postgres
    ip_postgres = myCloudOhio.getIP(postgres[0], "PublicIpAddress")

    # Edita o script para iniciar a intância django e insere o IP do Postgres
    editShellScript("./scripts/django.sh", "<replace me with ip>", ip_postgres)
    
    # Cria instância do Django
    django = myCloudNV.createInstance('t2.micro', myTagsDjango, sg_nv, chave_nv, open("./scripts/django.sh").read(), myCloudOhio.ami_ubuntu18_nv)
    
    # Edita novamente o script para remover o IP
    editShellScript("./scripts/django.sh", ip_postgres, "<replace me with ip>")
    
    # Cria AMI do Django
    # Mata a instância django
    # Cria novas instâncias com a AMI do django
    # Cria Load Balancer
    print("IP Público Django:", myCloudNV.getIP(django[0]))

def main():
    with open("./credentials/credentials.json", "r") as file:
        secrets = json.load(file)
    
    myCloudOhio = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                    secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                    region="us-east-2")

    chave = "botorafak"
    sg_name = "sec_kaki_OHIO"
    myCloudOhio.createRSA(chave)
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

    ip_postgres = myCloudOhio.getIP(inst1[0], "PrivateDnsName") 

    editShellScript("./scripts/django.sh", "<replace me with ip>", ip_postgres)
    myTags = {'ResourceType': 'instance','Tags': [{'Key': 'rafaDjango','Value': 'Django'},]}
    inst2 = myCloudOhio.createInstance('t2.micro', myTags, sg_name, chave, open("./scripts/django.sh").read(), myCloudOhio.ami_ubuntu18_ohio)
    print("\nInstancia Django:")
    myCloudOhio.getIP(inst2[0])
    editShellScript("./scripts/django.sh", ip_postgres, "<replace me with ip>")

def editShellScript(path, string1, string2):
    file_read = open(path, "rt")
    data = file_read.read()
    data = data.replace(string1, string2)
    file_read.close()
    file_write = open(path, "wt")
    file_write.write(data)
    file_write.close()

if __name__ == '__main__':
    teste_vital()