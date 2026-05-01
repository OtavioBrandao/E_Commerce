from flask import Flask, redirect, request, session, url_for
import requests

app = Flask(__name__)
app.secret_key = "atividade-ecommerce-simples"

# Dentro da rede Docker, os containers se comunicam pelo nome do servico.
CATALOGO_URL = "http://catalogo:5001"
FRETE_URL = "http://frete:5002"


def formatar_moeda(valor):
    """Formata valores no padrao brasileiro para exibir no HTML."""
    return f"R$ {valor:.2f}".replace(".", ",")


def pagina_base(titulo, conteudo):
    """Cria uma pagina HTML simples, sem framework frontend."""
    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titulo}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 0 20px;
                background: #f7f7f7;
                color: #222;
            }}
            h1, h2 {{
                color: #1f4f7a;
            }}
            .produto, .resultado, .erro, .carrinho {{
                background: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 16px;
                margin-bottom: 14px;
            }}
            .acoes {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                align-items: center;
            }}
            .botao {{
                display: inline-block;
                border: 1px solid #0b66c3;
                border-radius: 4px;
                padding: 8px 10px;
                background: #0b66c3;
                color: white;
            }}
            .botao-secundario {{
                background: white;
                color: #0b66c3;
            }}
            .erro {{
                border-color: #cc3d3d;
                color: #8a1f1f;
            }}
            a {{
                color: #0b66c3;
                text-decoration: none;
                font-weight: bold;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            select, button {{
                padding: 8px;
                margin-top: 8px;
            }}
            button {{
                cursor: pointer;
            }}
        </style>
    </head>
    <body>
        {conteudo}
    </body>
    </html>
    """


def buscar_json(url):
    """Chama outro microservico e centraliza o tratamento de erro de rede."""
    try:
        resposta = requests.get(url, timeout=5)
        return resposta.status_code, resposta.json()
    except requests.exceptions.RequestException:
        return None, {"erro": "Houve erro ao se comunicar com o servico."}
    except ValueError:
        return None, {"erro": "O servico retornou uma resposta invalida."}


def obter_carrinho():
    """Retorna a lista de ids dos produtos salvos no carrinho."""
    return session.get("carrinho", [])


def salvar_carrinho(carrinho):
    """Salva o carrinho na sessao do usuario."""
    session["carrinho"] = carrinho
    session.modified = True


def montar_resumo_carrinho(produtos):
    """Agrupa produtos repetidos para exibir quantidade e subtotal."""
    resumo = {}

    for produto in produtos:
        id_produto = produto["id"]

        if id_produto not in resumo:
            resumo[id_produto] = {
                "produto": produto,
                "quantidade": 0,
                "subtotal": 0
            }

        resumo[id_produto]["quantidade"] += 1
        resumo[id_produto]["subtotal"] += produto["preco"]

    return list(resumo.values())


def carregar_produtos_do_carrinho():
    """Busca no catalogo os detalhes dos produtos que estao no carrinho."""
    produtos = []

    for id_produto in obter_carrinho():
        status, produto = buscar_json(f"{CATALOGO_URL}/produtos/{id_produto}")

        if status is None:
            return None, "Houve erro ao se comunicar com o servico de catalogo."

        if status == 200:
            produtos.append(produto)

    return produtos, None


@app.route("/", methods=["GET"])
def inicio():
    status_produtos, produtos = buscar_json(f"{CATALOGO_URL}/produtos")
    status_cidades, cidades = buscar_json(f"{FRETE_URL}/cidades")

    if status_produtos is None:
        return pagina_base(
            "Erro de comunicacao",
            """
            <div class="erro">
                <h1>Erro de comunicacao</h1>
                <p>Houve erro ao se comunicar com o servico de catalogo.</p>
            </div>
            """
        ), 503

    if status_cidades is None:
        return pagina_base(
            "Erro de comunicacao",
            """
            <div class="erro">
                <h1>Erro de comunicacao</h1>
                <p>Houve erro ao se comunicar com o servico de frete.</p>
            </div>
            """
        ), 503

    lista_cidades = "".join(
        f"<li>{cidade['nome']} - {formatar_moeda(cidade['valor'])}</li>"
        for cidade in cidades
    )

    lista_produtos = ""
    for produto in produtos:
        lista_produtos += f"""
        <div class="produto">
            <h3>{produto["nome"]}</h3>
            <p>{produto["descricao"]}</p>
            <p><strong>Preco:</strong> {formatar_moeda(produto["preco"])}</p>
            <a class="botao" href="/adicionar/{produto["id"]}">Adicionar ao carrinho</a>
        </div>
        """

    quantidade_itens = len(obter_carrinho())

    conteudo = f"""
    <h1>Loja Simples de E-commerce</h1>
    <p>Exemplo didatico usando Flask, Docker e microservicos.</p>

    <div class="carrinho">
        <h2>Carrinho</h2>
        <p>Itens no carrinho: <strong>{quantidade_itens}</strong></p>
        <div class="acoes">
            <a class="botao" href="/carrinho">Ver carrinho</a>
            <a class="botao botao-secundario" href="/limpar-carrinho">Limpar carrinho</a>
        </div>
    </div>

    <h2>Produtos</h2>
    {lista_produtos}

    <h2>Cidades atendidas</h2>
    <ul>
        {lista_cidades}
    </ul>
    """

    return pagina_base("Loja Simples de E-commerce", conteudo)


@app.route("/adicionar/<id_produto>", methods=["GET"])
def adicionar_ao_carrinho(id_produto):
    status_produto, produto = buscar_json(f"{CATALOGO_URL}/produtos/{id_produto}")

    if status_produto is None:
        return pagina_base(
            "Erro de comunicacao",
            """
            <div class="erro">
                <h1>Erro de comunicacao</h1>
                <p>Houve erro ao se comunicar com o servico de catalogo.</p>
                <p><a href="/">Voltar para a loja</a></p>
            </div>
            """
        ), 503

    if status_produto == 404:
        return pagina_base(
            "Produto nao encontrado",
            f"""
            <div class="erro">
                <h1>Produto nao encontrado</h1>
                <p>Nao existe produto com o id <strong>{id_produto}</strong>.</p>
                <p><a href="/">Voltar para a loja</a></p>
            </div>
            """
        ), 404

    carrinho = obter_carrinho()
    carrinho.append(produto["id"])
    salvar_carrinho(carrinho)

    return redirect(url_for("carrinho"))


@app.route("/remover/<id_produto>", methods=["GET"])
def remover_do_carrinho(id_produto):
    carrinho = obter_carrinho()

    if id_produto in carrinho:
        carrinho.remove(id_produto)
        salvar_carrinho(carrinho)

    return redirect(url_for("carrinho"))


@app.route("/limpar-carrinho", methods=["GET"])
def limpar_carrinho():
    salvar_carrinho([])
    return redirect(url_for("inicio"))


@app.route("/carrinho", methods=["GET"])
def carrinho():
    produtos, erro = carregar_produtos_do_carrinho()
    status_cidades, cidades = buscar_json(f"{FRETE_URL}/cidades")

    if erro:
        return pagina_base(
            "Erro de comunicacao",
            f"""
            <div class="erro">
                <h1>Erro de comunicacao</h1>
                <p>{erro}</p>
                <p><a href="/">Voltar para a loja</a></p>
            </div>
            """
        ), 503

    if status_cidades is None:
        return pagina_base(
            "Erro de comunicacao",
            """
            <div class="erro">
                <h1>Erro de comunicacao</h1>
                <p>Houve erro ao se comunicar com o servico de frete.</p>
                <p><a href="/">Voltar para a loja</a></p>
            </div>
            """
        ), 503

    if not produtos:
        return pagina_base(
            "Carrinho vazio",
            """
            <h1>Carrinho</h1>
            <div class="carrinho">
                <p>Seu carrinho esta vazio.</p>
                <p><a href="/">Escolher produtos</a></p>
            </div>
            """
        )

    resumo = montar_resumo_carrinho(produtos)
    subtotal = sum(item["subtotal"] for item in resumo)

    linhas = ""
    for item in resumo:
        produto = item["produto"]
        linhas += f"""
        <tr>
            <td>{produto["nome"]}</td>
            <td>{item["quantidade"]}</td>
            <td>{formatar_moeda(produto["preco"])}</td>
            <td>{formatar_moeda(item["subtotal"])}</td>
            <td><a href="/remover/{produto["id"]}">Remover 1</a></td>
        </tr>
        """

    opcoes_cidades = "".join(
        f'<option value="{cidade["cidade"]}">{cidade["nome"]} - {formatar_moeda(cidade["valor"])}</option>'
        for cidade in cidades
    )

    conteudo = f"""
    <h1>Carrinho</h1>
    <div class="carrinho">
        <table border="1" cellpadding="8" cellspacing="0" width="100%">
            <thead>
                <tr>
                    <th>Produto</th>
                    <th>Qtd.</th>
                    <th>Preco</th>
                    <th>Subtotal</th>
                    <th>Acao</th>
                </tr>
            </thead>
            <tbody>
                {linhas}
            </tbody>
        </table>

        <h2>Subtotal: {formatar_moeda(subtotal)}</h2>

        <form action="/finalizar" method="get">
            <label for="cidade">Cidade para entrega:</label><br>
            <select id="cidade" name="cidade">
                {opcoes_cidades}
            </select>
            <button type="submit">Finalizar compra</button>
        </form>

        <p>
            <a href="/">Continuar comprando</a> |
            <a href="/limpar-carrinho">Limpar carrinho</a>
        </p>
    </div>
    """

    return pagina_base("Carrinho", conteudo)


@app.route("/finalizar", methods=["GET"])
def finalizar():
    cidade = request.args.get("cidade", "").lower()
    produtos, erro = carregar_produtos_do_carrinho()
    status_frete, frete = buscar_json(f"{FRETE_URL}/frete/{cidade}")

    if erro:
        return pagina_base(
            "Erro de comunicacao",
            f"""
            <div class="erro">
                <h1>Erro de comunicacao</h1>
                <p>{erro}</p>
                <p><a href="/carrinho">Voltar para o carrinho</a></p>
            </div>
            """
        ), 503

    if not produtos:
        return pagina_base(
            "Carrinho vazio",
            """
            <div class="erro">
                <h1>Carrinho vazio</h1>
                <p>Adicione pelo menos um produto antes de finalizar a compra.</p>
                <p><a href="/">Voltar para a loja</a></p>
            </div>
            """
        ), 400

    if status_frete is None:
        return pagina_base(
            "Erro de comunicacao",
            """
            <div class="erro">
                <h1>Erro de comunicacao</h1>
                <p>Houve erro ao se comunicar com o servico de frete.</p>
                <p><a href="/carrinho">Voltar para o carrinho</a></p>
            </div>
            """
        ), 503

    if status_frete == 404:
        return pagina_base(
            "Cidade nao encontrada",
            f"""
            <div class="erro">
                <h1>Cidade nao encontrada</h1>
                <p>Nao existe frete cadastrado para <strong>{cidade}</strong>.</p>
                <p><a href="/carrinho">Voltar para o carrinho</a></p>
            </div>
            """
        ), 404

    resumo = montar_resumo_carrinho(produtos)
    subtotal = sum(item["subtotal"] for item in resumo)
    total = subtotal + frete["valor"]

    itens = ""
    for item in resumo:
        produto = item["produto"]
        itens += f"""
        <li>
            {item["quantidade"]}x {produto["nome"]} -
            {formatar_moeda(item["subtotal"])}
        </li>
        """

    conteudo = f"""
    <h1>Resumo da compra</h1>
    <div class="resultado">
        <h2>Produtos</h2>
        <ul>
            {itens}
        </ul>
        <p><strong>Subtotal:</strong> {formatar_moeda(subtotal)}</p>
        <p><strong>Cidade:</strong> {frete["nome"]}</p>
        <p><strong>Frete:</strong> {formatar_moeda(frete["valor"])}</p>
        <h2>Total: {formatar_moeda(total)}</h2>
    </div>
    <p><a href="/carrinho">Voltar para o carrinho</a></p>
    <p><a href="/limpar-carrinho">Finalizar e limpar carrinho</a></p>
    """

    return pagina_base("Resumo da compra", conteudo)


@app.route("/comprar/<id_produto>/<cidade>", methods=["GET"])
def comprar(id_produto, cidade):
    status_produto, produto = buscar_json(f"{CATALOGO_URL}/produtos/{id_produto}")
    status_frete, frete = buscar_json(f"{FRETE_URL}/frete/{cidade}")

    if status_produto is None:
        return pagina_base(
            "Erro de comunicacao",
            """
            <div class="erro">
                <h1>Erro de comunicacao</h1>
                <p>Houve erro ao se comunicar com o servico de catalogo.</p>
                <p><a href="/">Voltar para a loja</a></p>
            </div>
            """
        ), 503

    if status_frete is None:
        return pagina_base(
            "Erro de comunicacao",
            """
            <div class="erro">
                <h1>Erro de comunicacao</h1>
                <p>Houve erro ao se comunicar com o servico de frete.</p>
                <p><a href="/">Voltar para a loja</a></p>
            </div>
            """
        ), 503

    if status_produto == 404:
        return pagina_base(
            "Produto nao encontrado",
            f"""
            <div class="erro">
                <h1>Produto nao encontrado</h1>
                <p>Nao existe produto com o id <strong>{id_produto}</strong>.</p>
                <p><a href="/">Voltar para a loja</a></p>
            </div>
            """
        ), 404

    if status_frete == 404:
        return pagina_base(
            "Cidade nao encontrada",
            f"""
            <div class="erro">
                <h1>Cidade nao encontrada</h1>
                <p>Nao existe frete cadastrado para <strong>{cidade}</strong>.</p>
                <p><a href="/">Voltar para a loja</a></p>
            </div>
            """
        ), 404

    total = produto["preco"] + frete["valor"]

    conteudo = f"""
    <h1>Resumo da compra</h1>
    <div class="resultado">
        <p><strong>Produto:</strong> {produto["nome"]}</p>
        <p><strong>Descricao:</strong> {produto["descricao"]}</p>
        <p><strong>Preco:</strong> {formatar_moeda(produto["preco"])}</p>
        <p><strong>Cidade:</strong> {frete["nome"]}</p>
        <p><strong>Frete:</strong> {formatar_moeda(frete["valor"])}</p>
        <h2>Total: {formatar_moeda(total)}</h2>
    </div>
    <p><a href="/">Voltar para a loja</a></p>
    """

    return pagina_base("Resumo da compra", conteudo)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
