from flask import Flask, jsonify, request
from flask_restful import Api
from web3 import Web3
import json
import os

app = Flask(__name__)
api = Api(app)

# Conectar-se ao Ganache (assumindo que o Ganache está rodando na porta padrão 8545)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Verificar a conexão
if w3.is_connected():
    print("Conectado ao Ganache com sucesso!")
else:
    print("Falha na conexão com Ganache.")

## Endereço do contrato ##
contract_address = '0x9CC81De7A749502D6B19Af7CD180BeBF3AD65B02'

## ABI do contrato ## 
 # Path arquivo abi
smart_contract_name = 'PoTFactory'
abi_file_path = f'SmartContract/artifacts/{smart_contract_name}_metadata.json'
 # Carregando a abi do arquivo json
with open(abi_file_path, 'r') as json_file:
    data = json.load(json_file)
    
abi = data['output']['abi']


# Obter instância do contrato
contract = w3.eth.contract(address=contract_address, abi=abi)

## Ganache accounts ##
# Endereço da controller
sender_address = w3.eth.accounts[1]

# Endereço do nó de saída
egress_address = w3.eth.accounts[2]
print('egress address: ' + egress_address)

# Endereço do auditor
auditor_address = w3.eth.accounts[3]
print('auditor address: ' + auditor_address)

# Função para chamar `echo` e emitir o evento
def call_echo(message):
    # Prepara a transação para chamar a função `echo`
    transaction = contract.functions.echo(message).build_transaction({
        'from': sender_address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(sender_address),
    })

    # Envia a transação
    tx_hash = w3.eth.send_transaction(transaction)

    # Espera a transação ser minerada
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Captura os logs do evento Echo
    logs = contract.events.Echo.create_filter(from_block=tx_receipt['blockNumber'], to_block=tx_receipt['blockNumber']).get_all_entries()

    # Extrai a mensagem do evento
    for log in logs:
        print(f"Mensagem do evento Echo: {log['args']['message']}")

    return w3.to_hex(tx_hash)

# Função para chamar `newFlow`
def call_newFlow(newFlowContract):
    # Prepara a transação para chamar a função `newFlow`
    transaction = contract.functions.newFlow(newFlowContract['flowId'], newFlowContract['edgeAddr'], newFlowContract['routeId']).build_transaction({
        'from': sender_address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(sender_address),
    })

    # Envia a transação
    tx_hash = w3.eth.send_transaction(transaction)

    return w3.to_hex(tx_hash)


# Função para chamar `setFlowProbeHash` e emitir o evento
def call_setFlowProbeHash(newRefSig):
    # Prepara a transação para chamar a função `setFlowProbeHash`
    transaction = contract.functions.setFlowProbeHash(newRefSig['flowId'], newRefSig['timestamp'], newRefSig['lightMultSig']).build_transaction({
        'from': sender_address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(sender_address),
    })

    # Envia a transação
    tx_hash = w3.eth.send_transaction(transaction)

    return w3.to_hex(tx_hash)

# Função para chamar `logProbe` e emitir o evento
def call_logFlowProbeHash(newlogProbe):
    # Prepara a transação para chamar a função `logProbe`
    transaction = contract.functions.logFlowProbeHash(newlogProbe['flowId'], newlogProbe['timestamp'], newlogProbe['lightMultSig']).build_transaction({
        'from': egress_address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(egress_address),
    })

    # Envia a transação
    tx_hash = w3.eth.send_transaction(transaction)

    return w3.to_hex(tx_hash)

def call_getFlowCompliance(flowId):
    # Chamar a função `getFlowCompliance`
    success, fail, nil = contract.functions.getFlowCompliance(flowId).call()    

    return success, fail, nil   

def verify_tx_status(tx_hash):
    tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
    if tx_receipt:
        if tx_receipt['status'] == 1:
            print("logProbe: A transação foi executada com sucesso.")
        else:
            print("logProbe: A transação falhou.")
    else:
        print("logProbe: A transação ainda está pendente.")


@app.route('/')
def home():
    return jsonify("Working")

@app.route('/hello')
def hello():
    data = call_echo("Hello")
    return jsonify(data)

@app.route('/deployFlowContract', methods=['POST'])
def deployFlowContract():
    data = request.get_json()

    if 'flowId' not in data or 'routeId' not in data or 'edgeAddr' not in data:
        return jsonify({"error": "Invalid Data"}), 400
    
    newFlowContract = {
        "flowId": data['flowId'],
        "routeId": data['routeId'],
        "edgeAddr": data['edgeAddr']
    }

    tx_hash = call_newFlow(newFlowContract)

    verify_tx_status(tx_hash)

    return jsonify(tx_hash), 201

@app.route('/setRefSig', methods=['POST'])
def setRefSig():
    data = request.get_json()

    required_keys = ['flowId', 'routeId', 'timestamp', 'lightMultSig']
    if not all(key in data for key in required_keys):   
        return jsonify({"error": "Invalid Data"}), 400
    
    newRefSig = {
        "flowId": data['flowId'],
        "routeId": data['routeId'],
        "timestamp": data['timestamp'],
        "lightMultSig": data['lightMultSig'],
    }

    tx_hash = call_setFlowProbeHash(newRefSig)

    verify_tx_status(tx_hash)

    return jsonify(tx_hash), 201

@app.route('/logProbe', methods=['POST'])
def logProbe():
    data = request.get_json()

    required_keys = ['flowId', 'routeId', 'timestamp', 'lightMultSig']
    if not all(key in data for key in required_keys):   
        return jsonify({"error": "Invalid Data"}), 400
    
    newlogProbe = {
        "flowId": data['flowId'],
        "routeId": data['routeId'],
        "timestamp": data['timestamp'],
        "lightMultSig": data['lightMultSig'],
    }

    tx_hash = call_logFlowProbeHash(newlogProbe)

    verify_tx_status(tx_hash)

    return jsonify(tx_hash), 201

@app.route('/getFlowCompliance/<flowId>', methods=['GET'])
def setFlowCompliance(flowId):
    success, fail, nil = call_getFlowCompliance(flowId)

    flowCompliance = {
        "success": success, 
        "fail": fail,
        "nil": nil, 
    }

    return jsonify(flowCompliance, 201)


if __name__ == "__main__":
    app.run(debug=True)
