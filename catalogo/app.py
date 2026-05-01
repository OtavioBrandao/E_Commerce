from flask import Flask, jsonify

app = Flask(__name__)

# Dados em memoria para manter o exemplo simples e didatico.
produtos = {
    "arroz": {
        "id": "arroz",
        "nome": "Arroz",
        "preco": 25.90,
        "descricao": "Pacote de arroz branco de 5 kg."
    },
    "feijao": {
        "id": "feijao",
        "nome": "Feijao",
        "preco": 9.50,
        "descricao": "Pacote de feijao carioca de 1 kg."
    },
    "macarrao": {
        "id": "macarrao",
        "nome": "Macarrao",
        "preco": 4.75,
        "descricao": "Pacote de macarrao espaguete de 500 g."
    },
    "cafe": {
        "id": "cafe",
        "nome": "Cafe",
        "preco": 16.20,
        "descricao": "Pacote de cafe torrado e moido de 500 g."
    }
}


@app.route("/produtos", methods=["GET"])
def listar_produtos():
    """Retorna todos os produtos disponiveis no catalogo."""
    return jsonify(list(produtos.values()))


@app.route("/produtos/<id_produto>", methods=["GET"])
def buscar_produto(id_produto):
    """Retorna um produto especifico pelo id."""
    produto = produtos.get(id_produto.lower())

    if produto is None:
        return jsonify({"erro": "Produto nao encontrado."}), 404

    return jsonify(produto)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
