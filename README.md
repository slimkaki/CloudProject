# Projeto de Cloud

Insper - Engenharia da Computação - 6° Semestre

Computação em Nuvem

**Aluno:** Rafael Almada

**Professor:** Raul Ikeda

**Anotações:** https://www.notion.so/Projeto-Cloud-e08415816e3e479ab61cb5fd7c57a074

_____

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

___

Problema: Checar se usuário cloud existe no postgresql

```sh
sudo su - postgres
postgrespsql -U postgres
\du
```

Túnel final:

```
ssh -i ./credentials/botorafak.pem ubuntu@<IP público Instância do Django> -L 8001:localhost:8080
```