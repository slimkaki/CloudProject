import boto3, time, json, paramiko, os
from CloudConfig import Cloud

def checkAndCreateRSA(myCloud: Cloud):
    """
    Classe desnecessária (?)
    Checa se existe já chave RSA
    Caso existe: retorna.
    Caso não existe: cria uma chave pública e outra privada
    """
    if (os.path.isfile("./credentials/id_rsa.pub")):
        return 
    else:
        privateKey, publicKey = myCloud.generateRSA()
        pub_file = open("./credentials/id_rsa.pub", "w")
        pub_file.write(publicKey.decode("utf-8"))
        pub_file.close()

        priv_file = open("./credentials/id_rsa", "w")
        priv_file.write(privateKey.decode("utf-8"))
        priv_file.close()
        return


def main():
    with open("./credentials/credentials.json", "r") as file:
        secrets = json.load(file)
    
    myCloud = Cloud(secrets["AWSUSER"], secrets["AWSPASS"], 
                    secrets["ACCESSKEYID"], secrets["SECRETACCESSKEY"])
    checkAndCreateRSA(myCloud)
    myTags = {'ResourceType': 'instance','Tags': [{'Key': 'rafaKeyTagTeste','Value': 'rafaValueTagTeste'},]}
    myCloud.createSecurityGroup("sec_kaki")
    secGroup =  myCloud.security_groups["sec_kaki"]["GroupId"]
    myCloud.createInstance("t2.micro", myTags, secGroup)
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
    # myCloud.describeInstances()
    # myCloud.terminateInstances()

if __name__ == '__main__':
    main()

