import boto3, time, json, paramiko
from CloudConfig import Cloud

def main():
    with open("./credentials/credentials.json", "r") as file:
        secrets = json.load(file)
    
    myCloud = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                    secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"])
    myTags = {'ResourceType': 'instance','Tags': [{'Key': 'rafaKeyTagTeste','Value': 'rafaValueTagTeste'},]}
    myCloud.createSecurityGroup("sec_kaki")
    secGroup =  myCloud.security_groups["sec_kaki"]["GroupId"]
    myCloud.createInstance("t2.micro", myTags, secGroup)
    # myCloud.createInstance("t2.micro", myTags, secGroup)
    print("sleeping for 30 seconds")
    t0 = time.time()
    while (time.time()-t0 < 30):
        print(str(int(time.time()-t0)) + " segundos", end="\r")
    print("just woke up!")
    # myCloud.describeInstances()
    # myCloud.terminateInstances()

if __name__ == '__main__':
    main()

