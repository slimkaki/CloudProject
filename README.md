# Projeto de Cloud

Insper - Engenharia da Computação - 6° Semestre

Computação em Nuvem - 2020.2

**Aluno:** Rafael Almada

**Professor:** Raul Ikeda

## Objetivo do projeto

Este projeto tem por objetivo implementar o deploy de uma aplicação que utiliza de *Django* e um banco de dados implementado em *postgresql* e os coloca online com um sistema de Load Balancing e Auto-Scaling.

Implementado para o sistema da *Amazon Web-Services* (AWS) e feito em Python, o código utiliza das funcionalidades da biblioteca boto3 para interagir com o sistema em nuvem.

### Como rodar o projeto

  O usuário deverá antes de rodar, colocar suas credenciais da AWS em um arquivo chamado *credentials.json* que ficará no diretório *./config/credentials/* e tem a o formato apresentado no arquivo *credentials_template.json*

  ```sh
  ubuntu@linux:~/CloudProject$ sudo chmod +x start.sh
  ```

  ```sh
  ubuntu@linux:~/CloudProject$ ./start.sh
  ```

### Operacionalização

A lógica por trás deste deploy está em uma série de etapas:

  1. Inicia sessão com as credenciais presentes no arquivo *./config/credentials/credentials.json*.

  2. Uma nova chave RSA é criada para cada uma das zonas, para o caso de o usuário necessitar, por algum mootivo, acessar alguma instância via ssh
  
  3. É criada uma instância em OHIO (zona "us-east-2") que inicia com o código presente no script *./config/scripts/postgres.sh*, que inicia a preparação do banco de dados em postgresql, innstalando o serviço na máquina, criando o usuário e o database para a aplicação. Espera-se a instância estar pronta para passar para a próxima etapa

  4. Uma instância em North Virginia (zona "us-east-1") é criada e iniciada com o script *"./config/scripts/django.sh"*, iniciando a aplicação django e deixando tudo pronto para a aplicação rodar.

  5. Após a instância do django estar preparada, é feita uma nova imagem a partir da mesma, podendo assim replicar a aplicação e preparando para a fase de load balancing e auto-scaling.

  > Ainda a terminar documentação...

### Distribuição do projeto:
```
.
├── README.md
├── config
│   ├── CloudConfig.py
│   ├── credentials
│   │   ├── boto_rafa_nv.pem
│   │   ├── boto_rafa_ohio.pem
│   │   ├── credentials.json
│   │   └── credentials_template.json
│   ├── main.py
│   ├── routine.py
│   └── scripts
│       ├── django.sh
│       └── postgres.sh
├── requirements.txt
└── start.sh
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

  **7.** Entrega: Até a última aula (27/Nov/2020).
