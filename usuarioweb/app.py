from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import hashlib
import uuid
import json
import os
import time

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para usar sessões e flash messages

# Função para gerar token baseado no ID do produto e índice da unidade
def gerar_token_produto(codigo_produto, unidade_idx):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{codigo_produto}_{unidade_idx}"))

# Função para gerar token do lote (NFe)
def gerar_token_lote(nfe_id):
    return hashlib.sha256(nfe_id.encode()).hexdigest()

# Lista de todos os status disponíveis em ordem
status_possiveis = [
    "em rota para o almoxarifado",
    "chegou no almoxarifado",
    "em fiscalização",
    "foi para a contabilidade",
    "etiquetado",
    "despachado para entrega"
]

# Simulação de dados
dados = {
    "nfe_id": "2924 0902 9931 3300 0131 5500 1000 0077 7014 7795 9596",
    "itens": [
        {"codigo_produto": "12084", "quantidade_produto": 1.00, "preco": 20.00},
        {"codigo_produto": "12992", "quantidade_produto": 1.00, "preco": 35.00},
        {"codigo_produto": "14332", "quantidade_produto": 3.00, "preco": 45.00},
        {"codigo_produto": "15420", "quantidade_produto": 2.00, "preco": 3.50},
        {"codigo_produto": "19858", "quantidade_produto": 5.00, "preco": 45.00},
        {"codigo_produto": "22501", "quantidade_produto": 1.00, "preco": 30.00}
    ]
}

# Criar um dicionário para armazenar os tokens e status
armazenamento_tokens = {}
token_lote = gerar_token_lote(dados["nfe_id"])
armazenamento_tokens['token_lote'] = token_lote

# Gerar tokens e definir status em ordem para cada unidade dos produtos
for index, item in enumerate(dados["itens"]):
    quantidade_produto = int(item["quantidade_produto"])
    for i in range(quantidade_produto):
        token_produto = gerar_token_produto(item["codigo_produto"], i)
        produto = {
            "codigo_produto": item["codigo_produto"],  # Código do produto sem o sufixo
            "quantidade_produto": 1,
            "preco": item["preco"],
            "token_produto": token_produto,
            "status": status_possiveis[index]  # Atribuir status em ordem
        }
        # Adicionar a unidade correta ao armazenamento
        armazenamento_tokens[f"{item['codigo_produto']}unidade{i+1}"] = produto

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verificar_nfe', methods=['POST'])
def verificar_nfe():
    nfe_id = request.form['nfe_id']
    if dados.get("nfe_id") == nfe_id:
        flash(f"Nota Fiscal {nfe_id} é válida.")
        salvar_tokens_arquivo()  # Salvar tokens automaticamente ao verificar a NFe válida
        return redirect(url_for('menu'))
    else:
        flash("Nota Fiscal inválida! Por favor, tente novamente.")
        return redirect(url_for('index'))

@app.route('/menu')
def menu():
    return render_template('menu.html', armazenamento_tokens=armazenamento_tokens)

@app.route('/buscar_status_token', methods=['POST'])
def buscar_status_token():
    token_produto = request.form['token_produto']
    produto = armazenamento_tokens.get(token_produto)
    
    if produto:
        # Extrair o número da unidade a partir da chave do token
        unidade = token_produto.split('unidade')[-1]
        return jsonify({
            "codigo_produto": f"{produto['codigo_produto']}unidade{unidade}",
            "status": produto['status']
        })
    else:
        return jsonify({"error": "Token não encontrado!"}), 404


def salvar_tokens_arquivo():
    with open('tokens_status_gerados.json', 'w') as arquivo_json:
        json.dump(armazenamento_tokens, arquivo_json, indent=4)

if __name__ == '__main__':
    app.run(debug=True, port=5005)
