############################
# Código desenvolvido por  #
#      Rafael Almada       #
#   github.com/slimkaki    #
# Engenharia da Computação #
# Insper - 6o Sem - 2020.2 #
############################

import boto3, time, json, os, sys
from CloudConfig import EC2Cloud, LoadBalancerConfig, AutoScaleConfig

def main(iterations):
    for i in range(int(iterations)):
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

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(iterations = sys.argv[1])
    else:
        main(iterations = 1)