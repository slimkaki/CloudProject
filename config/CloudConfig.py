############################
# Código desenvolvido por  #
#      Rafael Almada       #
#   github.com/slimkaki    #
# Engenharia da Computação #
# Insper - 6o Sem - 2020.2 #
############################

import boto3, json, time, os

class EC2Cloud(object):
    """
    Classe com o objetivo de criar a automatização do processo e dar deploy da aplicação na AWS
    """
    def __init__(self, AWS_USER, AWS_PASS, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region="us-east-1"):
        # Credenciais AWS
        self.USER = AWS_USER
        self.PASS = AWS_PASS
        self.ACCESSKEY = AWS_ACCESS_KEY_ID
        self.SECRETACCESSKEY = AWS_SECRET_ACCESS_KEY

        # Variáveis globais
        self.instances = {}
        self.security_groups = {}
        self.myIPs = []
        self.region = region
        self.ami_ubuntu18_nv = "ami-0817d428a6fb68645"
        self.ami_ubuntu18_ohio = "ami-0dd9f0e7df0f0a138"
        self.local_ami = {}
        self.subnets = []
        
        # Start session
        self.start()
    
    def start(self):
        """
        Inicia a sessão, os clients e os recursos.
        """
        print(f"Iniciando sessão em {self.region}!")
        self.session = boto3.session.Session(aws_access_key_id=self.ACCESSKEY,
                                        aws_secret_access_key=self.SECRETACCESSKEY,
                                        region_name=self.region)
        self.ec2_resource = self.session.resource('ec2')
        self.client = self.session.client('ec2', region_name=self.region)

    def cleanUp(self, tags, sg_name, key_name):
        # Vê todas as instâncias que foram feitas
        print(f"Limpando {self.region}...")
        inst = self.filterInstancesByTag(tags["Tags"][1]["Key"], tags["Tags"][1]["Value"])
        # Terminate instances
        if inst:
            print("Desligando instâncias existentes...", end="\r")
            self.terminateInstances(inst)
        # Apaga chaves da AWS
        try:
            keys = self.client.describe_key_pairs(KeyNames=[key_name])
            if keys:
                print("Apagando chaves existentes...        ", end="\r")
                for k in keys["KeyPairs"]:
                    self.client.delete_key_pair(KeyName=key_name)
        except:
            print("Key Pair não existe...               ", end="\r")
        
        # Apaga Security Group
        print("Apagando Security Groups existentes...", end="\r")
        try:
            sg = self.client.describe_security_groups(GroupNames=[sg_name])
            if sg:
                for sec in sg["SecurityGroups"]:
                    self.client.delete_security_group(GroupId=sec["GroupId"], GroupName=sec["GroupName"])
        except:
            print("SG não existe...                       ", end="\r")

        print("Tudo pronto!                              ")

    def createRSA(self, keyname):
        """
        Checa se já existe uma chave com o nome passado na função,
        caso não exista, é criado um par e salvo a .pem no diretório
        credentials.
        keyname: nome da chave a ser criada ou encontrada.
        """
        keypairs = self.client.describe_key_pairs()
        for i in keypairs["KeyPairs"]:
            if (i["KeyName"] == keyname):
                return
        key = self.client.create_key_pair(KeyName=keyname)
        self.path = "./credentials/{}.pem".format(keyname)

        if (os.path.isfile(self.path)):
            os.remove(self.path)
        priv_file = open(self.path, "w")
        priv_file.write(key['KeyMaterial'])
        priv_file.close()
        print("Chave disponível em:", self.path)
        return 

    def getIP(self, instance_id, ip_type="PublicIpAddress"):
        """
        Retorna o endereço IPv4 de uma instância a partir de seu id
        instance_id: id da instância
        ip_type: Ip público ("PublicIpAddress") ou privado ("PrivateIpAddress") ou "PrivateDnsName"
        """
        print("Adquirindo os IP's das instâncias... ")
        res = self.client.describe_instances(InstanceIds=[instance_id,])
        ip = res['Reservations'][0]['Instances'][0][ip_type]
        self.myIPs.append(ip)
        print(f"O ip é: {ip}")
        return ip 

    def createSecurityGroup(self, group_name, ports = [22]):
        """
        Cria um Grupo de Segurança.
        group_name: nome do grupo
        port (opcional): uma lista de todas as portas de acesso
        """
        IPperm = []
        for p in ports:
            IPperm.append({'IpProtocol': 'tcp','FromPort': p,'ToPort': p,'IpRanges':[{'CidrIp': '0.0.0.0/0'}]})
        print("Criando o grupo de segurança...")
        response = self.client.describe_vpcs()
        vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
        try:
            response = self.client.create_security_group(GroupName=group_name, Description="A boto3 sec group for rafa", VpcId=vpc_id)
            group_id = response['GroupId']
            self.client.authorize_security_group_ingress(GroupId=group_id, IpPermissions = IPperm)
            self.security_groups[group_name] = response
            print(f"Grupo de segurança {group_name} criado com sucesso em {self.region}")
        except Exception as e:
            print(f"Client Error: {e}")

    def createInstance(self, instanceType, tags, secGroup, myKey, ami, user_data = None, numInst = 1):
        """
        Cria uma nova instância.
        instanceType: flavor da instância (e.g. t2.micro, t2.large, ...)
        tags: as tags associadas à instância
        secGroup: o grupo de segurança da instância
        myKey: nome ("string") da chave de acesso da instância
        ami: Imagem para criar a instância
        numInst (opcional): número de instâncias iguais a serem criadas
        """
        print("Criando Instancia...")
        if (user_data == None):
            instance = self.ec2_resource.create_instances(ImageId=ami,
                                                          MinCount=numInst,
                                                          MaxCount=numInst,
                                                          InstanceType=instanceType,
                                                          KeyName=myKey,
                                                          TagSpecifications=[tags,],
                                                          SecurityGroupIds=[secGroup])
        else:
            instance = self.ec2_resource.create_instances(ImageId=ami,
                                                          MinCount=numInst,
                                                          MaxCount=numInst,
                                                          InstanceType=instanceType,
                                                          KeyName=myKey,
                                                          TagSpecifications=[tags,],
                                                          SecurityGroupIds=[secGroup],
                                                          UserData=user_data)
        new_insts = []
        for i in range(numInst):
            new_insts.append(instance[i].instance_id)
            self.instances[instance[i].instance_id] = instance[0]
        print("Aguardando instâncias...")
        instance_waiter = self.client.get_waiter('instance_running')
        instance_waiter.wait(InstanceIds=new_insts)
        print("Retomando atividades!")
        return new_insts

    def runInstancesFromNewAMI(self, instanceType, myKey, secGroup, ami, tags, numInst=1):
        conn = self.client.run_instances(InstanceType=instanceType,
                                         KeyName=myKey,
                                         MinCount=numInst,
                                         MaxCount=numInst,
                                         ImageId=ami,
                                         SecurityGroupIds=secGroup,
                                         TagSpecifications=tags)
        new_inst = []
        for i in conn["Instances"]:
            new_inst.append(i["InstanceId"])

        print("Aguardando instâncias...")
        instance_waiter = self.client.get_waiter('instance_running')
        instance_waiter.wait(InstanceIds=new_inst)
        print("Retomando atividades!")
        return new_inst
    
    def createAMIfromInstance(self, instance_id, name):
        """
        Cria uma imagem de uma instancia (AMI).
        instance_id: id da instância
        name: nome da imagem
        """
        print(f"Começando a criar imagem da instancia: {instance_id}")
        ami = self.client.create_image(InstanceId=instance_id, Name=name)
        self.local_ami[name] = ami['ImageId']
        print("Esperando para que a imagem fique pronta...")
        self.ec2_resource.Image(ami['ImageId']).wait_until_exists()
        waiter = self.client.get_waiter('image_available')
        waiter.wait(ImageIds=[ami['ImageId']])
        print("Imagem pronta!")
        return ami['ImageId']

    def generalWait(self, instance_id, wait_type):
        """
        Waiter generico.
        instance_id: id da instancia a ser esperada
        wait_type: motivo do wait
        """
        waiter = self.client.get_waiter(wait_type)
        waiter.wait(InstanceIds=[instance_id])

    def filterInstancesByTag(self, tag_key, tag_value):
        """
        Filtra instâncias por tag.
        tag_key: Chave da tag (e.g. "Name")
        tag_value: Valor da tag (e.g. "rafaPostgres")
        """
        custom_f = [{
            'Name': f'tag:{tag_key}',
            'Values': [tag_value]
        }]
        filtro_insts = []
        filtered = self.client.describe_instances(Filters=custom_f)
        for res in range(len(filtered["Reservations"])):
            for instance in filtered["Reservations"][res]["Instances"]:
                filtro_insts.append(instance["InstanceId"])

        return filtro_insts

    def getSubnets(self, inst_id):
        """
        Salva os ID's das subnets em uma lista
        inst_id: Lista com os id's das instâncias
        """
        for i in inst_id:
            self.subnets.append(self.instances[i].subnet_id)

    def terminateInstances(self, t_instances=None):
        """
        Encerra todas as instâncias que são passadas no argumento da função.
        t_instances (opcional): encerra todas instâncias com esses id's.
                                Lista de strings ou string com um ID único. 
        """
        instance_waiter = self.client.get_waiter('instance_terminated')
        self.client.terminate_instances(InstanceIds=t_instances)
        instance_waiter.wait(InstanceIds=t_instances)
            
class LoadBalancerConfig(object):
    """
    Classe destinada a administrar Load Balancer
    """
    def __init__(self, AWS_USER, AWS_PASS, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region, elb_name):
        # Credencias AWS
        self.USER = AWS_USER
        self.PASS = AWS_PASS
        self.ACCESSKEY = AWS_ACCESS_KEY_ID
        self.SECRETACCESSKEY = AWS_SECRET_ACCESS_KEY

        # Variáveis globais:
        self.region = region
        self.myLoadBalancers = []
        self.elb_name = elb_name

        # Start client
        self.start()

    def start(self):
        """
        Inicia o client els (Elastic Load Balancer)
        """
        print("Iniciando Load Balancer...")
        self.client = boto3.client('elb', 
                                   region_name=self.region, 
                                   aws_access_key_id=self.ACCESSKEY,
                                   aws_secret_access_key=self.SECRETACCESSKEY)

    def cleanLoadBalancers(self):
        """
        Deleta todos os load balancers que possuem 
        """
        print("Limpando Load Balancers...")
        try:
            self.client.delete_load_balancer(LoadBalancerName=self.elb_name)
        except:
            print(f"Nenhum Load Balancer chamado {self.elb_name} encontrado")

    def createLoadBalancer(self, subnets, security_group):
        """
        Cria um Load Balancer
        name: nome do Load Balancer
        subnets: Lista com os id's das subnets das instâncias
        sg: Security Group do Load Balancer 
        """
        print("Criando Load Balancer...")
        self.DNSname = self.client.create_load_balancer(LoadBalancerName=self.elb_name,
                                                        Listeners=[{'Protocol': 'HTTP',
                                                                    'LoadBalancerPort': 80,
                                                                    'InstancePort': 8080},],
                                                        Subnets=subnets,
                                                        SecurityGroups=[security_group])

    def addInstances(self, name, instances_id):
        """
        Adiciona instâncias ao Load Balancer
        name: Nome do Load Balancer
        instances_id: ID da instância ou lista de IDs de instâncias a serem adicionadas.
        """
        print("Adicionando instâncias ao load balancer...")
        if (type(instances_id) != list):
            instances_id = [instances_id]
        my_inst = []
        for i in instances_id:
            my_inst.append({'InstanceId': i})

        self.client.register_instances_with_load_balancer(LoadBalancerName=name,
                                                          Instances=my_inst)

        waiter = self.client.get_waiter('instance_deregistered')
        waiter.wait(LoadBalancerName=name, Instances=my_inst)
        print("Instâncias adicionadas!")

    def removeInstances(self, name, instances_id):
        """
        Remove instâncias do Load Balancer
        name: Nome do Load Balancer
        instances_id: ID da instância ou lista de IDs de instâncias a serem removidas.
        """
        print("Remvendo instâncias do load balancer...")
        if (type(instances_id) != list):
            instances_id = [instances_id]
        my_inst = []
        for i in instances_id:
            my_inst.append({'InstanceId': i})
        self.client.deregister_instances_from_load_balancer(LoadBalancerName=name,
                                                          Instances=my_inst)
        waiter = self.client.get_waiter('instance_deregistered')
        waiter.wait(LoadBalancerName=name, Instances=my_inst)
        print("Instâncias removidas!")

class AutoScaleConfig(object):
    """
    Classe destinada a administrar o auto-scaling
    """
    def __init__(self, AWS_USER, AWS_PASS, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, region, as_name):
        # Credencias AWS
        self.USER = AWS_USER
        self.PASS = AWS_PASS
        self.ACCESSKEY = AWS_ACCESS_KEY_ID
        self.SECRETACCESSKEY = AWS_SECRET_ACCESS_KEY

        # Variáveis globais:
        self.region = region
        self.name = as_name
        self.start()

    def start(self):
        self.client = boto3.client('autoscaling',
                                   region_name=self.region, 
                                   aws_access_key_id=self.ACCESSKEY,
                                   aws_secret_access_key=self.SECRETACCESSKEY)

    def createAutoScalingGroup(self, inst, lb_name, tags, maxSize=5):
        if (type(inst) == list):
            inst = inst[0]
        self.client.create_auto_scaling_group(AutoScalingGroupName=self.name,
                                              MinSize=1,
                                              MaxSize=maxSize,
                                              InstanceId=inst,
                                              DesiredCapacity=1,
                                              LoadBalancerNames=[lb_name])

    def deleteAutoScalingGroup(self):
        try:
            self.client.delete_auto_scaling_group(AutoScalingGroupName=self.name,
                                            ForceDelete=True)
            print(f"Auto-Scaling Group de nome {self.name} foi deletado!")
        except:
            print("Nenhum Auto-Scaling Group foi encontrado!")

    def deleteLaunchConfig(self):
        try:
            self.client.delete_launch_configuration(LaunchConfigurationName=self.name)
            print("Launch Configuration do Auto Scaling Group foi deletada!")
        except:
            print("Não foi possível encontrar o Launch Configuration do Auto Scaling Group")

    def attachInstances(self, instances):
        self.client.attach_instances(InstanceIds=instances,
                                     AutoScalingGroupName=self.auto_scale_name)