############################
# Código desenvolvido por  #
#      Rafael Almada       #
#   github.com/slimkaki    #
# Engenharia da Computação #
# Insper - 6o Sem - 2020.2 #
############################

import boto3, time, json, os
from CloudConfig import EC2Cloud, LoadBalancerConfig, AutoScaleConfig

def main():
    # Carrega as credenciais
    with open("./credentials/credentials.json", "r") as file:
        secrets = json.load(file)

    # Algumas variáveis globais
    ## Nomes de chaves
    chave_nv = "boto_rafa_nv"      # Chave RSA NORTH VIRGINIA
    chave_ohio = "boto_rafa_ohio"  # Chave RSA OHIO

    ## Nomes dos Security Groups
    sg_nv = "sec_rafa_NV"          # Grupo de segurança de NORTH VIRGINIA
    sg_ohio = "sec_rafa_OHIO"      # Grupo de segurança de OHIO

    ## Tags
    ### Tag para as instâncias Django em North Virginia
    myTagsDjango = {
                'ResourceType': 'instance',
                    'Tags': [{
                            'Key': 'owner',
                            'Value': 'rafaelama'
                            },
                            {
                            'Key': 'Name',
                            'Value': 'rafaDjango'
                            },]
                        }
    
    ### Tag para as instâncias Postgres em Ohio
    myTagsPostGres = {
                'ResourceType': 'instance',
                    'Tags': [{
                        'Key': 'owner',
                        'Value': 'rafaelama'
                        },
                        {
                        'Key': 'Name',
                        'Value': 'rafaPostgres'
                        },]
                    }
    ### Nome do Auto Scaling
    auto_scale_name_NV = "rafaAutoScalerNV"

    ### Nome do Load Balancer
    loadBalancer_name_NV = "rafa-load-balancer"

    # Inicia o Load Balancer
    myLoadBalancer = LoadBalancerConfig(secrets["AWSUSER"], secrets["AWSPASS"], 
                                        secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                                        region="us-east-1", elb_name=loadBalancer_name_NV)
    
    # Limpa Load Balancer
    myLoadBalancer.cleanLoadBalancers()

    # Inicia o Auto-Scaling Group
    myAutoScalerNV = AutoScaleConfig(secrets["AWSUSER"], secrets["AWSPASS"], 
                                   secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                                   region="us-east-1", as_name=auto_scale_name_NV)

    # Limpa Auto-Scale
    myAutoScalerNV.deleteAutoScalingGroup()
    myAutoScalerNV.deleteLaunchConfig()

    # Inicia sessão em NORTH VIRGINIA
    myCloudNV = EC2Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                      secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                      region="us-east-1")

    # Realiza a limpeza da AWS North Virginia
    myCloudNV.cleanUp(myTagsDjango, sg_nv, chave_nv)

    # Inicia sessão em OHIO
    myCloudOhio = EC2Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                        secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                        region="us-east-2")

    # Realiza a limpeza da AWS Ohio
    myCloudOhio.cleanUp(myTagsPostGres, sg_ohio, chave_ohio)

    # Cria as chaves de acesso
    myCloudOhio.createRSA(chave_ohio)
    myCloudNV.createRSA(chave_nv)
    
    # Cria os grupos de segurança
    myCloudOhio.createSecurityGroup(sg_ohio, [22, 5432]) # Postgresql Server
    myCloudNV.createSecurityGroup(sg_nv, [22, 8080, 80]) # Django server

    # Cria a primeira instância do Postgres em Ohio
    postgres = myCloudOhio.createInstance('t2.micro', myTagsPostGres, sg_ohio, chave_ohio, myCloudOhio.ami_ubuntu18_ohio, open("./scripts/postgres.sh").read())
    
    # Guarda o IP público do Postgres
    ip_postgres = myCloudOhio.getIP(postgres[0], "PublicIpAddress")

    # Edita o script para iniciar a intância django e insere o IP do Postgres
    editShellScript("./scripts/django.sh", "<replace me with ip>", ip_postgres)
    
    # Cria instância do Django
    django = myCloudNV.createInstance('t2.micro', myTagsDjango, sg_nv, chave_nv, myCloudOhio.ami_ubuntu18_nv, open("./scripts/django.sh").read())
    
    # Edita novamente o script para remover o IP
    editShellScript("./scripts/django.sh", ip_postgres, "<replace me with ip>")
    
    # Espera a instância
    # myCloudOhio.filterInstancesByTag("Name", "rafaPostgres")
    myCloudNV.generalWait(django[0], "instance_status_ok")

    # Guarda o ID das subnets das instâncias
    myCloudNV.getSubnets(django)

    # Cria o Load Balancer
    myLoadBalancer.createLoadBalancer(myCloudNV.subnets, myCloudNV.security_groups[sg_nv]["GroupId"])
    
    # Adiciona as instâncias no Load Balancer
    myLoadBalancer.addInstances(loadBalancer_name_NV, django)

    # Cria o Grupo de Auto Scaling
    myAutoScalerNV.createAutoScalingGroup(django, loadBalancer_name_NV, myTagsDjango)
    
    # Cria novas instâncias com a AMI do django
    # Cria Load Balancer
    print("\nDNS Load Balancer:", myLoadBalancer.DNSname["DNSName"])
    print(f"\n Para acessar: http://{myLoadBalancer.DNSname['DNSName']}/tasks")
    print(f"(será necessário esperar algo entre 5 e 15 minutos)")

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