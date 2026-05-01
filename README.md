# E-commerce com Microservicos, Flask e Docker

Este projeto e uma atividade didatica de um pequeno e-commerce usando 3 microservicos em Python com Flask. Cada servico roda em seu proprio container Docker e se comunica pela rede criada pelo Docker Compose.

O objetivo principal e demonstrar o conceito de microservicos de forma simples: servicos separados, responsabilidades separadas e comunicacao via HTTP.

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

## Papel de cada microservico

### 1. Orquestrador

O microservico orquestrador roda na porta `5000` e e responsavel por coordenar os outros servicos.

Ele:

- Exibe a interface web da loja na rota `/`.
- Busca produtos no servico de catalogo.
- Busca cidades e valores de frete no servico de frete.
- Permite adicionar produtos ao carrinho.
- Exibe o carrinho na rota `/carrinho`.
- Finaliza a compra na rota `/finalizar?cidade=<cidade>`.
- Calcula o total da compra somando subtotal dos produtos e frete.

Dentro do Docker Compose, ele chama os outros servicos usando:

```text
http://catalogo:5001
http://frete:5002
```

Isso e importante porque, entre containers, nao usamos `localhost`. Usamos o nome do servico definido no `docker-compose.yml`.

### 2. Catalogo

O microservico de catalogo roda na porta `5001` e guarda os produtos em memoria.

Rotas:

- `GET /produtos`: retorna todos os produtos.
- `GET /produtos/<id_produto>`: retorna um produto especifico.

Produtos cadastrados:

- `arroz`
- `feijao`
- `macarrao`
- `cafe`

### 3. Frete

O microservico de frete roda na porta `5002` e guarda os valores de frete em memoria.

Rotas:

- `GET /cidades`: retorna todas as cidades disponiveis.
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

Esse comando constroi as imagens e inicia os 3 containers:

- `orquestrador`
- `catalogo`
- `frete`

## Como acessar a aplicacao

Depois que os containers estiverem rodando, acesse a loja pelo navegador:

```text
http://localhost:5000
```

## Como testar as APIs separadamente

Catalogo de produtos:

```text
http://localhost:5001/produtos
```

Cidades disponiveis para frete:

```text
http://localhost:5002/cidades
```

Buscar um produto especifico:

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

1. Buscar os produtos do carrinho no microservico de catalogo.
2. Buscar o frete da cidade escolhida no microservico de frete.
3. Somar o subtotal dos produtos com o frete.
4. Exibir o resumo da compra em HTML.

Tambem e possivel testar diretamente uma compra antiga, com apenas um produto:

```text
http://localhost:5000/comprar/arroz/maceio
```

## Como parar os containers

Para parar e remover os containers criados pelo Docker Compose, execute:

```bash
docker compose down
```

## Rodando manualmente sem Docker Compose

Esta etapa e opcional. Ela mostra como criar a rede, construir as imagens e executar cada container manualmente.

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

O projeto possui mensagens amigaveis para casos como:

- Produto inexistente.
- Cidade inexistente.
- Falha de comunicacao entre o orquestrador e algum microservico.

Exemplos:

```text
http://localhost:5000/comprar/produto-inexistente/maceio
http://localhost:5000/comprar/arroz/cidade-inexistente
http://localhost:5000/finalizar?cidade=cidade-inexistente
```

## Observacoes

- Nao ha banco de dados.
- Nao ha autenticacao.
- Nao ha Kubernetes.
- Nao ha frontend separado.
- Os dados ficam em dicionarios em memoria.
- Cada microservico possui seu proprio `Dockerfile`.
- Cada aplicacao Flask roda com `host="0.0.0.0"`.
