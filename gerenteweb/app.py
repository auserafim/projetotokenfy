from flask import Flask, render_template, redirect, url_for, request
import json
import os

app = Flask(__name__)

# Define the status order for products
status_order = [
    "em rota para o almoxarifado",
    "chegou no almoxarifado",
    "em fiscalização",
    "foi para a contabilidade",
    "etiquetado",
    "despachado para entrega"
]


@app.route('/view_in_almoxarifado')
def view_in_almoxarifado():
    if not os.path.exists('tokensoutput.json'):
        return "Tokens not found. Please generate them first."

    with open('tokensoutput.json', 'r') as json_file:
        tokens = json.load(json_file)

    # Filter tokens with status "chegou no almoxarifado"
    filtered_tokens = {key: value for key, value in tokens.items() if value.get('status') == 'chegou no almoxarifado'}

    # Get the first 10 tokens (or fewer if less are available)
    tokens_to_display = list(filtered_tokens.keys())[:10]

    return render_template('in_almoxarifado.html', tokens=tokens_to_display)

# Route to view all product statuses
@app.route('/view_status')
def view_status():
    if not os.path.exists('tokensoutput.json'):
        return "Tokens not found. Please generate them first by visiting /generate_tokens."

    with open('tokensoutput.json', 'r') as json_file:
        tokens = json.load(json_file)
    return render_template('status.html', tokens=tokens)

# Route to advance the status of a product
@app.route('/advance_product/<token_key>', methods=['POST'])
def advance_product(token_key):
    if not os.path.exists('tokensoutput.json'):
        return "Tokens not found. Please generate them first."

    with open('tokensoutput.json', 'r') as json_file:
        tokens = json.load(json_file)

    if token_key in tokens:
        current_status = tokens[token_key]['status']
        current_index = status_order.index(current_status)

        if current_index < len(status_order) - 1:
            # Advance to the next status in the order
            next_status = status_order[current_index + 1]
            tokens[token_key]['status'] = next_status

            # Save the updated tokens to the JSON file
            with open('tokensoutput.json', 'w') as json_file:
                json.dump(tokens, json_file, ensure_ascii=False, indent=4)

        return redirect(url_for('view_status'))  # Reload the page after updating the status
    else:
        return "Token not found", 404

# Route to generate tokens
@app.route('/generate_tokens', methods=['POST'])
def generate_tokens():
    products_data = [
        {"codigo_produto": "12084", "quantidade_produto": 1, "preco": 20.0, "status": "em rota para o almoxarifado"},
        {"codigo_produto": "12992", "quantidade_produto": 1, "preco": 35.0, "status": "em rota para o almoxarifado"},
        {"codigo_produto": "14332", "quantidade_produto": 3, "preco": 45.0, "status": "em rota para o almoxarifado"},
        {"codigo_produto": "15420", "quantidade_produto": 2, "preco": 3.5, "status": "em rota para o almoxarifado"},
        {"codigo_produto": "19858", "quantidade_produto": 5, "preco": 45.0, "status": "em rota para o almoxarifado"},
        {"codigo_produto": "22501", "quantidade_produto": 1, "preco": 30.0, "status": "em rota para o almoxarifado"}
    ]
    
    tokens_output = {}
    for product in products_data:
        codigo_produto = product['codigo_produto']
        quantidade_produto = product['quantidade_produto']
        status = product['status']
        token_produto = f"{codigo_produto}_1"  # Example token

        tokens_output[token_produto] = {
            "codigo_produto": codigo_produto,
            "quantidade_produto": quantidade_produto,
            "status": status,
        }
    
    with open('tokensoutput.json', 'w') as json_file:
        json.dump(tokens_output, json_file, indent=4)
    
    return redirect(url_for('view_status'))

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' ,port=5007)
