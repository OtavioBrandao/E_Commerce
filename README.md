# E-commerce com Microserviços, Flask e Docker

Este projeto é uma atividade didática de um pequeno e-commerce usando 3 microserviços em Python com Flask. Cada serviço roda em seu próprio container Docker e se comunica pela rede criada pelo Docker Compose.

O objetivo principal é demonstrar o conceito de microserviços de forma simples: serviços separados, responsabilidades separadas e comunicação via HTTP.

## Estrutura do projeto

```text
ecommerce-microservices/
|
├── docker-compose.yml
├── README.md
|
├── orquestrador/
|   ├── app.py
|   ├── requirements.txt
|   └── Dockerfile
|
├── catalogo/
|   ├── app.py
|   ├── requirements.txt
|   └── Dockerfile
|
└── frete/
    ├── app.py
    ├── requirements.txt
    └── Dockerfile
```

## Papel de cada microserviço

### 1. Orquestrador

O microserviço orquestrador roda na porta `5000` e é responsável por coordenar os outros serviços.

Ele:

- Exibe a interface web da loja na rota `/`.
- Busca produtos no serviço de catálogo.
- Busca cidades e valores de frete no serviço de frete.
- Permite adicionar produtos ao carrinho.
- Exibe o carrinho na rota `/carrinho`.
- Finaliza a compra na rota `/finalizar?cidade=<cidade>`.
- Calcula o total da compra somando o subtotal dos produtos com o frete.

Dentro do Docker Compose, ele chama os outros serviços usando:

```text
http://catalogo:5001
http://frete:5002
```

Isso é importante porque, entre containers, não usamos `localhost`. Usamos o nome do serviço definido no `docker-compose.yml`.

### 2. Catálogo

O microserviço de catálogo roda na porta `5001` e guarda os produtos em memória.

Rotas:

- `GET /produtos`: retorna todos os produtos.
- `GET /produtos/<id_produto>`: retorna um produto específico.

Produtos cadastrados:

- `arroz`
- `feijao`
- `macarrao`
- `cafe`

### 3. Frete

O microserviço de frete roda na porta `5002` e guarda os valores de frete em memória.

Rotas:

- `GET /cidades`: retorna todas as cidades disponíveis.
- `GET /frete/<cidade>`: retorna o valor do frete para uma cidade.

Cidades cadastradas:

- `maceio`
- `recife`
- `sao-paulo`
- `rio-de-janeiro`

## Como rodar com Docker Compose

Na pasta raiz do projeto, execute:

```bash
docker compose up --build
```

Esse comando constrói as imagens e inicia os 3 containers:

- `orquestrador`
- `catalogo`
- `frete`

## Como acessar a aplicação

Depois que os containers estiverem rodando, acesse a loja pelo navegador:

```text
http://localhost:5000
```

## Como testar as APIs separadamente

Catálogo de produtos:

```text
http://localhost:5001/produtos
```

Cidades disponíveis para frete:

```text
http://localhost:5002/cidades
```

Buscar um produto específico:

```text
http://localhost:5001/produtos/arroz
```

Buscar o frete de uma cidade:

```text
http://localhost:5002/frete/maceio
```

## Como testar uma compra

Pelo navegador, acesse a loja:

```text
http://localhost:5000
```

Na tela inicial:

1. Clique em `Adicionar ao carrinho` em um ou mais produtos.
2. Acesse o carrinho.
3. Escolha a cidade para entrega.
4. Clique em `Finalizar compra`.

O orquestrador vai:

1. Buscar os produtos do carrinho no microserviço de catálogo.
2. Buscar o frete da cidade escolhida no microserviço de frete.
3. Somar o subtotal dos produtos com o frete.
4. Exibir o resumo da compra em HTML.

Também é possível testar diretamente uma compra antiga, com apenas um produto:

```text
http://localhost:5000/comprar/arroz/maceio
```

## Como parar os containers

Para parar e remover os containers criados pelo Docker Compose, execute:

```bash
docker compose down
```

## Rodando manualmente sem Docker Compose

Esta etapa é opcional. Ela mostra como criar a rede, construir as imagens e executar cada container manualmente.

Crie a rede Docker:

```bash
docker network create ecommerce-net
```

Construa as imagens:

```bash
docker build -t catalogo ./catalogo
docker build -t frete ./frete
docker build -t orquestrador ./orquestrador
```

Execute os containers na mesma rede:

```bash
docker run -d -p 5001:5001 --network ecommerce-net --name catalogo catalogo
docker run -d -p 5002:5002 --network ecommerce-net --name frete frete
docker run -d -p 5000:5000 --network ecommerce-net --name orquestrador orquestrador
```

Depois acesse:

```text
http://localhost:5000
```

Para remover os containers criados manualmente:

```bash
docker stop orquestrador catalogo frete
docker rm orquestrador catalogo frete
```

## Tratamento de erros

O projeto possui mensagens amigáveis para casos como:

- Produto inexistente.
- Cidade inexistente.
- Falha de comunicação entre o orquestrador e algum microserviço.

Exemplos:

```text
http://localhost:5000/comprar/produto-inexistente/maceio
http://localhost:5000/comprar/arroz/cidade-inexistente
http://localhost:5000/finalizar?cidade=cidade-inexistente
```

## Observações

- Não há banco de dados.
- Não há autenticação.
- Não há Kubernetes.
- Não há frontend separado.
- Os dados ficam em dicionários em memória.
- Cada microserviço possui seu próprio `Dockerfile`.
- Cada aplicação Flask roda com `host="0.0.0.0"`.
