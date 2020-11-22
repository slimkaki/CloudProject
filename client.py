############################
# Código desenvolvido por  #
#      Rafael Almada       #
#   github.com/slimkaki    #
# Engenharia da Computação #
# Insper - 6o Sem - 2020.2 #
############################

import datetime, requests, json

def client(url, loop=True):
    print("====================================")
    print("Bem vindo ao client da API de Tasks!")
    print("====================================")
    desc = {"get all": "Retorna todas as tasks existentes",
            "get <id task>": "Retorna uma task única com id especificado",
            "post": "Cria uma task nova com os parametros especificados",
            "delete <id task>": "Deleta uma task especificada pelo id",
            "delete all": "Deleta todas as tasks",
            "update <id task>": "Atualiza uma task",
            "url": "Inserir nova url da API",
            "exit": "Sair deste client",
            "quit": "Sair deste client",
            "help": "Mostra os comandos possíveis"}
    print("\nOs comandos disponíveis são os seguintes:")

    for i in desc:
        print("\t>", i)
        print(f"\t\t{desc[i]}\n")

    while loop:
        entrada = input("> ")

        if (entrada.split()[0] == "get" and len(entrada.split()) > 1):
            if (entrada.split()[1] == "all"):
                get_all = url + "get_all"
                response = requests.get(get_all)
                print(response.json())
            elif (entrada.split()[1].isdigit()):
                get_id = url + f"get_single/{entrada.split()[1]}"
                try:
                    response = requests.get(get_id)
                    print(response.json())
                except:
                    print("Essa task não existe!")
            else:
                print(f"Comando '{entrada}' não identificado.")

        elif (entrada == "post"):
            print("Qual o título da nova task?")
            title = input("> ")
            now = str(datetime.datetime.now())
            now_date = now.split(" ")[0]
            now_time = now.split(" ")[1].split(".")[0]
            pub_date = now_date + "T" + now_time + "Z"
            print("Qual a descrição da nova task?")
            description = input("> ")
            body = {"title": title, "pub_date": pub_date, "description": description}
            post = url + "post"
            try:
                response = requests.post(post, data=json.dumps(body))
                print("Task criada com sucesso!")
            except:
                print("Erro na criação da task!")
        
        elif(entrada.split()[0] == "delete" and len(entrada.split()) > 1):
            if (entrada.split()[1] == "all"):
                print("Deletando todas as tasks")
                try:
                    delete = url + "delete_all"
                    response = requests.delete(delete)
                except:
                    print("Não foi possivel deletar todas as tasks!")
            elif (entrada.split()[1].isdigit()):
                print(f"Deletando task {entrada.split()[1]}")
                try:
                    delete = url + "delete/" + str(entrada.split()[1])
                    response = requests.delete(delete)
                except:
                    print(f"Não foi possível deletar a task {entrada.split()[1]}!")
            else:
                print(f"Comando '{entrada}' não identificado.")
        
        elif (entrada.split()[0] == "update" and len(entrada.split()) > 1):
            if (entrada.split()[1].isdigit()):
                print(f"Alterando task {entrada.split()[1]}:")
                print("Qual o novo título da task?")
                title = input("> ")
                now = str(datetime.datetime.now())
                now_date = now.split(" ")[0]
                now_time = now.split(" ")[1].split(".")[0]
                pub_date = now_date + "T" + now_time + "Z"
                print("Qual a nova descrição da task?")
                description = input("> ")
                my_update = url + "update/" + str(entrada.split()[1])
                body = {"title": title, "pub_date": pub_date, "description": description}
                try:
                    response = requests.put(my_update, data=json.dumps(body))
                    print(f"Task {entrada.split()[1]} alterada com sucesso!")
                except:
                    print("Não foi possível alterar a task em questão!")
            else:
                print(f"Comando '{entrada}' não identificado.")
        elif (entrada == "url"):
            print("Insira a nova url:")
            url = input("> ")
            url = url + "/tasks/"

        elif (entrada == "quit" or entrada == "exit"):
            print("Até mais!")
            loop = False
        elif (entrada == "help"):
            print("Os comandos disponíveis são os seguintes:")
            for i in desc:
                print("\t>", i)
                print(f"\t\t{desc[i]}\n")
        else:
            print(f"Comando '{entrada}' não identificado.")
            
if __name__ == '__main__':
    url = "http://rafa-load-balancer-1033912535.us-east-1.elb.amazonaws.com/" + "/tasks/"
    client(url)