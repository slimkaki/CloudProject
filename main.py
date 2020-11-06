import boto3
import json
import time

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
        self.region = region
        self.ami_ubuntu18 = "ami-0817d428a6fb68645"
        
        # Start session
        self.deployApplication()
    
    def deployApplication(self):
        self.keyPairing()
        self.ec2_resource = self.session.resource('ec2')

    def keyPairing(self):
        print("Time to log in!")
        self.session = boto3.session.Session(aws_access_key_id=self.ACCESSKEY,
                                        aws_secret_access_key=self.SECRETACCESSKEY,
                                        region_name=self.region)
        
    def describeInstances(self):
        print("Describing instances: ")
        response = self.ec2_resource.describe_instances()
        print(response)

    def getAlreadyDeployedInstances(self):
        """
        - NOT DONE -
        Atualiza o dicionário de instâncias que estão lançadas na AWS
        """

        return 0

    def createInstance(self, instanceType, tags):
        print("Criando Instancia:")
        instance = self.ec2_resource.create_instances(ImageId=self.ami_ubuntu18,
                                                      MinCount=1,
                                                      MaxCount=1,
                                                      InstanceType=instanceType,
                                                      KeyName="rafak",
                                                      TagSpecifications=[tags,])

        self.instances[instance[0].instance_id] = instance[0]
        print(self.instances)
    
    def terminateInstances(self):
        for i in self.instances:
            print(f"Terminating instance: '{i}'")
             # self.instances[instance_id].terminate()
            terminator = self.instances[i].terminate()
            # print("\t", terminator)
            print(terminator["TerminatingInstances"][0]["CurrentState"]["Name"])
            print(terminator["TerminatingInstances"][0]["CurrentState"]["Code"])
    


if __name__ == '__main__':
    with open("credentials.json", "r") as file:
        secrets = json.load(file)
    
    myCloud = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                    secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"])
    myTags = {'ResourceType': 'instance','Tags': [{'Key': 'rafaKeyTagTeste','Value': 'rafaValueTagTeste'},]}
    myCloud.createInstance("t2.micro", myTags)
    print("sleeping for 10 seconds")
    time.sleep(10)
    print("just woke up!")
    myCloud.terminateInstance()
    # myCloud.describeInstances()