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
    # Inicia sessão em NORTH VIRGINIA
    myCloudNV = EC2Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                      secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                      region="us-east-1")

    # Realiza a limpeza da AWS
    myCloudNV.cleanUp(myTagsDjango, sg_nv, chave_nv)

    # Inicia sessão em OHIO
    myCloudOhio = EC2Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                        secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                        region="us-east-2")

    # Realiza a limpeza da AWS
    myCloudOhio.cleanUp(myTagsPostGres, sg_ohio, chave_ohio)

    # Inicia o Load Balancer
    myLoadBalancer = LoadBalancerConfig(secrets["AWSUSER"], secrets["AWSPASS"], 
                                        secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                                        region="us-east-1")

    myAutoScaler = AutoScaleConfig(secrets["AWSUSER"], secrets["AWSPASS"], 
                                   secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                                   region="us-east-1")

    # Cria as chaves de acesso
    myCloudOhio.createRSA(chave_ohio)
    myCloudNV.createRSA(chave_nv)
    
    # Cria os grupos de segurança
    myCloudOhio.createSecurityGroup(sg_ohio, [22, 5432]) # Postgresql Server
    myCloudNV.createSecurityGroup(sg_nv, [22, 8080]) # Django server

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
    
    # Cria AMI do Django
    # django_ami_id = myCloudNV.createAMIfromInstance(django[0], "rafa_django_ami")
    # print("AMI Django:", django_ami_id)

    # myTagsDjango2 = {'ResourceType': 'instance','Tags': [{'Key': 'owner', 'Value': 'rafaelama'},{'Key': 'Name','Value': 'rafaDjango2'},]}
    # django2 = myCloudNV.createInstance('t2.micro', myTagsDjango2, sg_nv, chave_nv, django_ami_id)
    
    insts = [django, django2]
    loadBalancerNV = "RafaLoadBalancer"
    myCloudNV.getSubnets(insts)
    myLoadBalancer.createLoadBalancer(loadBalancerNV, myCloudNV.subnets, myCloudNV.security_groups[sg_nv]["GroupId"])
    
    myLoadBalancer.addInstances(loadBalancerNV, insts)
    # Cria novas instâncias com a AMI do django
    # Cria Load Balancer
    print("\nIP Público Django:", myCloudNV.getIP(django[0]))

def testCleanUp():
    with open("./credentials/credentials.json", "r") as file:
        secrets = json.load(file)

    # Inicia sessão em NORTH VIRGINIA
    myCloudNV = EC2Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                      secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                      region="us-east-1")

    sg_nv = "sec_rafa_NV"
    chave_nv = "boto_rafa_nv"
    myCloudNV.createRSA(chave_nv)
    myCloudNV.createSecurityGroup(sg_nv, [22, 8080])
    myTagsDjango = {'ResourceType': 'instance','Tags': [{'Key': 'owner', 'Value': 'rafaelama'},{'Key': 'Name','Value': 'rafaDjango'},]}
    a = myCloudNV.createInstance('t2.micro', myTagsDjango, sg_nv, chave_nv, myCloudNV.ami_ubuntu18_nv)
    myCloudNV.generalWait(a[0], "instance_status_ok")
    myCloudNV.cleanUp(myTagsDjango, sg_nv, chave_nv)

def test_loadBalancer():
    with open("./credentials/credentials.json", "r") as file:
        secrets = json.load(file)
    myLoadBalancer = LoadBalancerConfig(secrets["AWSUSER"], secrets["AWSPASS"], 
                                        secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"],
                                        regions=["us-east-1"])
    loadBalancerNV = "RafaLoadBalancer"
    insts = ["i-02898328875efd8d8", "i-0f603cfc135ab4218"]
    myLoadBalancer.createLoadBalancer(loadBalancerNV, "sg-0e9b298c3b1fa1a43")
    myLoadBalancer.addInstances(loadBalancerNV, insts)

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