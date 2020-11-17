import boto3, time, json, paramiko, os
from CloudConfig import Cloud, LoadBalancerConfig

def main():
    # Carrega as credenciais
    with open("./credentials/credentials.json", "r") as file:
        secrets = json.load(file)

    # Inicia sessão em NORTH VIRGINIA
    myCloudNV = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                      secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                      region="us-east-1")

    # Inicia sessão em OHIO
    myCloudOhio = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                        secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                        region="us-east-2")



    myLoadBalancer = LoadBalancerConfig(secrets["AWSUSER"], secrets["AWSPASS"], 
                                        secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                                        regions=["us-east-1","us-east-2"])

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
    myTagsPostGres = {'ResourceType': 'instance','Tags': [{'Key': 'owner', 'Value': 'rafaelama'},{'Key': 'Name','Value': 'rafaPostgres'},]}
    myTagsDjango = {'ResourceType': 'instance','Tags': [{'Key': 'owner', 'Value': 'rafaelama'},{'Key': 'Name','Value': 'rafaDjango'},]}

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
    
    # Espera a instância
    # myCloudOhio.filterInstancesByTag("Name", "rafaPostgres")
    myCloudNV.generalWait(django[0], "instance_status_ok")
    
    # Cria AMI do Django
    django_ami_id = myCloudNV.createAMIfromInstance(django[0], "rafa_django_ami")
    print("AMI Django:", django_ami_id)

    django2 = myCloudNV.createInstance('t2.micro', myTagsDjango, sg_nv, chave_nv, open("./scripts/django.sh").read(), myCloudOhio.ami_ubuntu18_nv)
    
    insts = [django, django2]
    loadBalancerNV = "RafaLoadBalancer"
    myLoadBalancer.createLoadBalancer(loadBalancerNV, myCloudNV.security_groups[sg_nv])
    
    myLoadBalancer.addInstances(loadBalancerNV, insts)
    # Cria novas instâncias com a AMI do django
    # Cria Load Balancer
    print("\nIP Público Django:", myCloudNV.getIP(django[0]))

def editShellScript(path, string1, string2):
    file_read = open(path, "rt")
    data = file_read.read()
    data = data.replace(string1, string2)
    file_read.close()
    file_write = open(path, "wt")
    file_write.write(data)
    file_write.close()

if __name__ == '__main__':
    main()