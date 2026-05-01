from flask import Flask, jsonify

app = Flask(__name__)

# Valores de frete em memoria para algumas cidades.
fretes = {
    "maceio": {
        "cidade": "maceio",
        "nome": "Maceio",
        "valor": 12.00
    },
    "recife": {
        "cidade": "recife",
        "nome": "Recife",
        "valor": 15.00
    },
    "sao-paulo": {
        "cidade": "sao-paulo",
        "nome": "Sao Paulo",
        "valor": 25.00
    },
    "rio-de-janeiro": {
        "cidade": "rio-de-janeiro",
        "nome": "Rio de Janeiro",
        "valor": 22.00
    }
}


@app.route("/cidades", methods=["GET"])
def listar_cidades():
    """Retorna todas as cidades atendidas pelo servico de frete."""
    return jsonify(list(fretes.values()))


@app.route("/frete/<cidade>", methods=["GET"])
def calcular_frete(cidade):
    """Retorna o valor do frete para uma cidade."""
    frete = fretes.get(cidade.lower())

    if frete is None:
        return jsonify({"erro": "Cidade nao encontrada."}), 404

    return jsonify(frete)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
