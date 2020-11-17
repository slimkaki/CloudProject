import boto3, json, time, paramiko, os

class Cloud(object):
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
        print("Criando o grupo de segurança:")
        response = self.client.describe_vpcs()
        vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
        try:
            response = self.client.create_security_group(GroupName=group_name, Description="A boto3 sec group for rafa", VpcId=vpc_id)
            group_id = response['GroupId']
            self.client.authorize_security_group_ingress(GroupId=group_id, IpPermissions = IPperm)
            self.security_groups[group_name] = response
        except Exception as e:
            print(f"Client Error: {e}")

    def createInstance(self, instanceType, tags, secGroup, myKey, user_data, ami, numInst = 1):
        """
        Cria uma nova instância.
        instanceType: flavor da instância (e.g. t2.micro, t2.large, ...)
        tags: as tags associadas à instância
        secGroup: o grupo de segurança da instância
        myKey: nome ("string") da chave de acesso da instância
        ami: Imagem para criar a instância
        numInst (opcional): número de instâncias iguais a serem criadas
        """
        print("Criando Instancia:")
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
            print(instance[0])
        print("Aguardando instâncias...")
        instance_waiter = self.client.get_waiter('instance_running')
        instance_waiter.wait(InstanceIds=new_insts)
        print("Retomando atividades!")
        return new_insts
    
    def createAMIfromInstance(self, instance_id, name):
        """
        Cria uma imagem de uma instancia (AMI).
        instance_id: id da instância
        name: nome da imagem
        """
        ami = self.client.create_image(InstanceId=instance_id, Name=name)
        self.local_ami[name] = ami['ImageId']
        image = self.ec2_resource.get_all_images(image_ids=[ami['ImageId']][0])
        print("Esperando para que a imagem fique pronta...")
        self.ec2_resource.Image(ami['ImageId']).wait_until_exists()
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
        for instance in filtered["Reservations"][0]["Instances"]:
            filtro_insts.append(instance["InstanceId"])

        return filtro_insts

    def terminateInstances(self, t_instances=None):
        """
        Encerra todas as instâncias que são passadas no argumento da função.
        t_instances (opcional): encerra todas instâncias com esses id's
        """
        if t_instances == None:
            t_instances = self.instances
        t_inst = []
        instance_waiter = self.client.get_waiter('instance_terminated')
        for i in t_instances:
            print(f"Terminating instance: '{i}'")
             # self.instances[instance_id].terminate()
            terminator = t_instances[i].terminate()
            print(terminator["TerminatingInstances"][0]["CurrentState"]["Name"])
            print(terminator["TerminatingInstances"][0]["CurrentState"]["Code"])
            # print("\t", terminator)
            t_inst.append(t_instances[i])
        instance_waiter.wait(InstanceIds=t_inst)
            
class LoadBalancerConfig(object):
    """
    Classe destinada a administrar Load Balancer
    """
    def __init__(self, AWS_USER, AWS_PASS, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, regions):
        # Credencias AWS
        self.USER = AWS_USER
        self.PASS = AWS_PASS
        self.ACCESSKEY = AWS_ACCESS_KEY_ID
        self.SECRETACCESSKEY = AWS_SECRET_ACCESS_KEY

        # Variáveis globais:
        self.regions = regions
        self.myLoadBalancers = []

        # Start client
        self.start()

    def start(self):
        """
        Inicia o client els (Elastic Load Balancer)
        """
        self.client = boto3.client('elb')

    def createLoadBalancer(self, name, security_group):
        """
        Cria um Load Balancer
        name: nome do Load Balancer
        sg: Security Group do Load Balancer 
        """
        print("Criando Load Balancer...")
        self.client.create_load_balancer(LoadBalancerName=name,
                                            AvailabilityZones=self.regions,
                                            SecurityGroups=[security_group])

    def addInstances(self, name, instances_id):
        """
        Adiciona instâncias ao Load Balancer
        name: Nome do Load Balancer
        instances_id: ID da instância ou lista de IDs de instâncias a serem adicionadas.
        """
        if (type(instances_id) != list):
            instances_id = [instances_id]
        my_inst = []
        for i in instances_id:
            my_inst.append({'InstanceId': i})

        self.client.register_instances_with_load_balancer(LoadBalancerName=name,
                                                          Instances=my_inst)

    def removeInstances(self, name, instances_id):
        """
        Remove instâncias do Load Balancer
        name: Nome do Load Balancer
        instances_id: ID da instância ou lista de IDs de instâncias a serem removidas.
        """
        if (type(instances_id) != list):
            instances_id = [instances_id]
        my_inst = []
        for i in instances_id:
            my_inst.append({'InstanceId': i})
        self.client.deregister_instances_from_load_balancer(LoadBalancerName=name,
                                                          Instances=my_inst)