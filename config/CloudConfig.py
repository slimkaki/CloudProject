import boto3, json, time, paramiko, os

class Cloud(object):
    """
    Classe com o objetivo de criar a automatização do processo e dar deploy da aplicação na AWS
    """
    def __init__(self, AWS_USER, AWS_PASS, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,region = "us-east-1"):
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
        self.ami_ubuntu18 = "ami-0817d428a6fb68645"
        
        # Start session
        self.start()
    
    def start(self):
        self.keyPairing()
        self.ec2_resource = self.session.resource('ec2')
        self.client = self.session.client('ec2')

    def keyPairing(self):
        print("Time to log in!")
        self.session = boto3.session.Session(aws_access_key_id=self.ACCESSKEY,
                                        aws_secret_access_key=self.SECRETACCESSKEY,
                                        region_name=self.region)

    def loadRSA(self, keyname):
        keypairs = self.client.describe_key_pairs()
        for i in keypairs["KeyPairs"]:
            print(i)
            if (i["KeyName"] == keyname):
                print("CHAVE EXISTE")
                return
        print("Não achei a chave :(")
        print("Criando uma nova chave")
        key = self.client.create_key_pair(KeyName=keyname)
        self.path = "./credentials/{}.pem".format(keyname)

        if (os.path.isfile(self.path)):
            os.remove(self.path)
        priv_file = open(self.path, "w")
        priv_file.write(key['KeyMaterial'])
        priv_file.close()
        print("Chave disponível em:", self.path)
        return

    def getPublicIP(self, instance_id):
        print("Getting IPs of the instances... ")
        res = self.client.describe_instances(InstanceIds=[instance_id,])
        ip = res['Reservations'][0]['Instances'][0]['PublicIpAddress']
        self.myIPs.append(ip)
        print(f"O ip é: {ip}")
        return ip 

    def createSecurityGroup(self, group_name, ports = [22]):
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
            # print("response sec group: ", response)
        except Exception as e:
            print(f"Client Error: {e}")

    def createInstance(self, instanceType, tags, secGroup, myKey, numInst = 1):
        print("Criando Instancia:")
        instance = self.ec2_resource.create_instances(ImageId=self.ami_ubuntu18,
                                                      MinCount=numInst,
                                                      MaxCount=numInst,
                                                      InstanceType=instanceType,
                                                      KeyName=myKey,
                                                      TagSpecifications=[tags,],
                                                      SecurityGroupIds=[secGroup])

        for i in range(numInst):
            self.instances[instance[i].instance_id] = instance[0]
            print(instance[0])
    
    def connectToInstance(self, instance_ip):
        print(f"Time to connect via ssh to {instance_ip}...")
        key = paramiko.RSAKey.from_private_key_file(self.path)
        pclient = paramiko.SSHClient()
        pclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect/ssh to an instance
        try:
            # Here 'ubuntu' is user name and 'instance_ip' is public IP of EC2
            pclient.connect(hostname=str(instance_ip), username="ubuntu", pkey=key)
            print("Conectei!")
            # Execute a command(cmd) after connecting/ssh to an instance
            stdin, stdout, stderr = pclient.exec_command("ls -la")
            print(stdout.read())
            stdin, stdout, stderr = pclient.exec_command("whoami")
            print(stdout.read())

            # close the client connection once the job is done
            pclient.close()
        except Exception as e:
            print(e)

    def terminateInstances(self):
        for i in self.instances:
            print(f"Terminating instance: '{i}'")
             # self.instances[instance_id].terminate()
            terminator = self.instances[i].terminate()
            # print("\t", terminator)
            print(terminator["TerminatingInstances"][0]["CurrentState"]["Name"])
            print(terminator["TerminatingInstances"][0]["CurrentState"]["Code"])