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
    print(f"URL atual: {url}")
    desc = {"get all": "Retorna todas as tasks existentes",
            "get <id task>": "Retorna uma task única com id especificado",
            "post": "Cria uma task nova com os parametros especificados",
            "delete <id task>": "Deleta uma task especificada pelo id",
            "delete all": "Deleta todas as tasks",
            "update <id task>": "Atualiza uma task",
            "url": "Inserir nova url da API (Inserir a url com o '/tasks/')",
            "exit": "Sair deste client",
            "quit": "Sair deste client",
            "help": "Mostra os comandos possíveis"}
    print("\nOs comandos disponíveis são os seguintes:")

    for i in desc:
        print("\t>", i)
        print(f"\t\t{desc[i]}\n")

    while loop:
        entrada = input("tasks-api> ")

        if (entrada.split()[0] == "get" and len(entrada.split()) > 1):
            if (entrada.split()[1] == "all"):
                get_all = url + "get_all"
                response = requests.get(get_all)
                for task in response.json():
                    print(f"\033[1m\033[96mTask {task['id']}:\033[0m")
                    for item in task:
                        if item == "id":
                            continue
                        print(f"\t\033[91m{item}:\033[0m {task[item]}")
            elif (entrada.split()[1].isdigit()):
                get_id = url + f"get_single/{entrada.split()[1]}"
                # print(f"get_id = {get_id}")
                try:
                    response = requests.get(get_id)
                    print(f"\033[1m\033[96mTask {response.json()['id']}:\033[0m")
                    for item in response.json():
                        if item == "id":
                            continue
                        print(f"\t\033[91m{item}:\033[0m {response.json()[item]}")
                except:
                    print("\033[1m\033[91mEssa task não existe!\033[0m")
            else:
                print(f"Comando '{entrada}' não identificado.")

        elif (entrada == "post"):
            print("Qual o título da nova task?")
            title = input("titulo> ")
            now = str(datetime.datetime.now())
            now_date = now.split(" ")[0]
            now_time = now.split(" ")[1].split(".")[0]
            pub_date = now_date + "T" + now_time + "Z"
            print("Qual a descrição da nova task?")
            description = input("descricao> ")
            body = {"title": title, "pub_date": pub_date, "description": description}
            post = url + "post"
            try:
                response = requests.post(post, data=json.dumps(body))
                print("Task criada com sucesso!")
            except:
                print("\033[1m\033[91mErro na criação da task!\033[0m")
        
        elif(entrada.split()[0] == "delete" and len(entrada.split()) > 1):
            if (entrada.split()[1] == "all"):
                print("Deletando todas as tasks")
                try:
                    delete = url + "delete_all"
                    response = requests.delete(delete)
                except:
                    print("\033[1m\033[91mNão foi possivel deletar todas as tasks!\033[0m")
            elif (entrada.split()[1].isdigit()):
                print(f"Deletando task {entrada.split()[1]}")
                try:
                    delete = url + "delete/" + str(entrada.split()[1])
                    response = requests.delete(delete)
                except:
                    print(f"\033[1m\033[91mNão foi possível deletar a task {entrada.split()[1]}!\033[0m")
            else:
                print(f"Comando '{entrada}' não identificado.")
        
        elif (entrada.split()[0] == "update" and len(entrada.split()) > 1):
            if (entrada.split()[1].isdigit()):
                print(f"Alterando task {entrada.split()[1]}:")
                print("Qual o novo título da task?")
                title = input("tasks-api> ")
                now = str(datetime.datetime.now())
                now_date = now.split(" ")[0]
                now_time = now.split(" ")[1].split(".")[0]
                pub_date = now_date + "T" + now_time + "Z"
                print("Qual a nova descrição da task?")
                description = input("tasks-api> ")
                my_update = url + "update/" + str(entrada.split()[1])
                body = {"title": title, "pub_date": pub_date, "description": description}
                try:
                    response = requests.put(my_update, data=json.dumps(body))
                    print(f"Task {entrada.split()[1]} alterada com sucesso!")
                except:
                    print("\033[1m\033[91mNão foi possível alterar a task em questão!\033[0m")
            else:
                print(f"\033[1m\033[91mComando '{entrada}' não identificado.\033[0m")
        elif (entrada == "url"):
            print("Insira a nova url:")
            url = input("nova-url> ")
            # url = url + "/tasks/"

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
    url = "http://rafa-load-balancer-1231070759.us-east-1.elb.amazonaws.com/" + "tasks/"
    client(url)