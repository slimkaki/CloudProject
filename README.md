# Projeto de Cloud

Insper - Engenharia da Computação - 6° Semestre

Computação em Nuvem - 2020.2

**Aluno:** Rafael Almada

**Professor:** Raul Ikeda

## Objetivo do projeto

Este projeto tem por objetivo implementar o deploy de uma aplicação que utiliza de *Django* e um banco de dados implementado em *postgresql* e os coloca online com um sistema de Load Balancing e Auto-Scaling.

Implementado para o sistema da *Amazon Web-Services* (AWS) e feito em Python, o código utiliza das funcionalidades da biblioteca boto3 para interagir com o sistema em nuvem.

### Aplicação REST API

A aplicação escolhida para este projeto, como já especificado antes, foi um código em Django e um servidor Postgres.

O código que roda no Django, com todas as operações da api pode ser encontrado no repositório **http://github.com/slimkaki/tasks**.

### Como rodar o projeto

  O usuário deverá antes de rodar, colocar suas credenciais da AWS em um arquivo chamado *credentials.json* que ficará no diretório *./config/credentials/* e tem a o formato apresentado no arquivo *credentials_template.json*

Primeiramente o usuário deverá tornar o arquivo install executável:

  ```bash
  ubuntu@linux:~/CloudProject$ sudo chmod +x install
  ```

Em seguida deverá rodar o install, que tornará os outros scripts também executáveis

  ```bash
  ubuntu@linux:~/CloudProject$ ./install
  ```

Assim poderá rodar o start para rodar o projeto em sua conta da AWS:

  ```bash
  ubuntu@linux:~/CloudProject$ ./start
  ```

Após o projeto estar rodando, ele poderá rodar o client para se comunicar com a api:

  ```bash
  ubuntu@linux:~/CloudProject$ ./client-tasks <url/tasks>
  ```

  > OBS: É preciso passar a url (DNS do Load Balancer) com o /tasks como argumento do client. Essa url completa é printada no fim da execução do script `start`


Se desejar encerrar tudo o que foi feito e limpar sua AWS, poderá rodar o script clean_aws:

  ```bash
  ubuntu@linux:~/CloudProject$ ./clean_aws
  ```

### Operacionalização

A lógica por trás deste deploy está em uma série de etapas:

  1. Inicia sessão com as credenciais presentes no arquivo *./config/credentials/credentials.json*.

  2. Limpa todas as Instâncias, Security Groups, Chaves, Load Balancers e Auto-Scaling Groups que já estão criados com os nomes e tags usados neste projeto.

  3. Uma nova chave RSA é criada para cada uma das zonas, para o caso de o usuário necessitar, por algum mootivo, acessar alguma instância via ssh.
  
  4. É criada uma instância em OHIO (zona "us-east-2") que inicia com o código presente no script *./config/scripts/postgres.sh*, que inicia a preparação do banco de dados em postgresql, innstalando o serviço na máquina, criando o usuário e o database para a aplicação. Espera-se a instância estar pronta para passar para a próxima etapa.

  5. Uma instância em North Virginia (zona "us-east-1") é criada e iniciada com o script *"./config/scripts/django.sh"*, iniciando a aplicação django e deixando tudo pronto para a aplicação rodar.

  6. Após a instância do django estar pronta para uso, é criado o Load Balancer no servidor da North Virginia, para balacearos acessos ao client do django.

  7. Em seguida é criado o AutoScaling Group em North Virginia, para que assim a aplicação se torne automaticamente escalável conforme sua necessidade de uso. 

  8. Após cerca de 5 a 10 minutos do término da execução do script **start.sh**, é possível acessar o link entregue no terminal com um DNS direcionado ao endpoint */tasks*.

  9. Agora basta rodar o script do client com o seguinte comando:

  ```bash
  ubuntu@linux:~/CloudProject$ ./client.sh
  ```

### Distribuição do projeto:
```
.
├── README.md
├── clean_aws
├── client.py
├── client-tasks
├── config
│   ├── CloudConfig.py
│   ├── clean.py
│   ├── credentials
│   │   ├── boto_rafa_nv.pem
│   │   ├── boto_rafa_ohio.pem
│   │   ├── credentials.json
│   │   └── credentials_template.json
│   ├── routine.py
│   └── scripts
│       ├── django.sh
│       └── postgres.sh
├── install
└── start
```

___

Requisitos do projeto:

  • O projeto é estritamente individual.
  
  • O aluno terá livre escolha sobre as funcionalidades do projeto.
  
  • Um sistema ORM multi-cloud com Load Balancer e Autoscalling.
  
  **1.** Implementar comunicação via REST API.

  **2.** Autenticação de usuário stateless.

  **3.** Sistema de log das atividades.

  **4.** Possuir um aplicação cliente.

  **5.** Possuir um script de implantação automático (sem intervenção manual).

  **6.** Utilizar uma linguagem de programação de livre escolha, embora seja sugerido usar uma que tenha
  bibliotecas para manipulação de Cloud prontas.

  **7.** Entrega: Último commmit até dia 02/12 às 07h30.
