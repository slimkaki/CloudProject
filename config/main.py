import boto3, time, json, paramiko, os
from CloudConfig import Cloud

def main():
    with open("./credentials/credentials.json", "r") as file:
        secrets = json.load(file)
    
    myCloud = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                    secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"])
    # checkAndCreateRSA(myCloud)
    chave = "botorafak"
    myCloud.loadRSA(chave)
    myTags = {'ResourceType': 'instance','Tags': [{'Key': 'rafaKeyTagTeste','Value': 'rafaValueTagTeste'},]}
    myCloud.createSecurityGroup("sec_kaki")
    secGroup =  myCloud.security_groups["sec_kaki"]["GroupId"]
    myCloud.createInstance("t2.micro", myTags, secGroup, chave)
    # myCloud.createInstance("t2.micro", myTags, secGroup)
    print("sleeping for 120 seconds")
    t0 = time.time()
    while (time.time()-t0 < 120):
        print("> " + str(int(120-(time.time()-t0))) + " segundos ", end="\r")
    print("just woke up!")
    for i in myCloud.instances:
        myCloud.getPublicIP(i)
    print("myIPs = ", myCloud.myIPs)
    myCloud.connectToInstance(myCloud.myIPs[0])
    
    myCloud.terminateInstances()

if __name__ == '__main__':
    main()

