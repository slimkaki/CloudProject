import boto3
import json

class Cloud(object):
    """
    Classe com o objetivo de criar a automatização do processo e dar deploy da aplicação na AWS
    """
    def __init__(self, AWS_USER, AWS_PASS, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,region = "us-east-1"):
        self.USER = AWS_USER
        self.PASS = AWS_PASS
        self.ACCESSKEY = AWS_ACCESS_KEY_ID
        self.SECRETACCESSKEY = AWS_SECRET_ACCESS_KEY
        self.region = region
        self.keyPairing()
        self.ec2_session = self.session.client('ec2')
        self.ami_ubuntu18 = "ami-0817d428a6fb68645"

    def keyPairing(self):
        print("Time to log in!")
        self.session = boto3.session.Session(aws_access_key_id=self.ACCESSKEY,
                                        aws_secret_access_key=self.SECRETACCESSKEY,
                                        region_name=self.region)
        return
        
    def describeInstances(self):
        print("Describing instances: ")
        response = self.ec2_session.describe_instances()
        print(response)

    def createInstance(self):
        # ec2client = self.session.client('ec2')
        self.ec2_session.run_instances(ImageId=self.ami_ubuntu18, MinCount=1, MaxCount=1)
    
    def deployApplication(self):
        return deploy

if __name__ == '__main__':
    with open("credentials.json", "r") as file:
        secrets = json.load(file)
    
    myCloud = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                    secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"])
    myCloud.createInstance()
    myCloud.describeInstances()