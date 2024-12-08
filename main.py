from flask import Flask, jsonify, request
from flask_restful import Api
from web3 import Web3

app = Flask(__name__)
api = Api(app)

# Conectar-se ao Ganache (assumindo que o Ganache está rodando na porta padrão 8545)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Verificar a conexão
if w3.is_connected():
    print("Conectado ao Ganache com sucesso!")
else:
    print("Falha na conexão com Ganache.")

# Endereço do contrato
contract_address = '0x965FA8d25f77a54D3f00fF051248C3BEC164435e'

# ABI do contrato 
abi = [
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "string",
				"name": "message",
				"type": "string"
			}
		],
		"name": "Echo",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "Hello",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "pure",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "message",
				"type": "string"
			}
		],
		"name": "echo",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"name": "flowAddr",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "flowId",
				"type": "string"
			}
		],
		"name": "getFlowCompliance",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "success",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "fail",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "nil",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "flowId",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "id_x",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "hash",
				"type": "string"
			}
		],
		"name": "logFlowProbeHash",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "flowId",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "egress_edgeAddr",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "routeId",
				"type": "string"
			}
		],
		"name": "newFlow",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "flowId",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "id_x",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "hash",
				"type": "string"
			}
		],
		"name": "setFlowProbeHash",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "flowId",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "newRouteID",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "newEgressEdge",
				"type": "address"
			}
		],
		"name": "setRouteId",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]

# Obter instância do contrato
contract = w3.eth.contract(address=contract_address, abi=abi)

# Endereço da controller
sender_address = "0x62fE12d237d76eb19Fca7b66C91440659c04627e"
# Chave privada para assinar a transação (não usar em produção sem proteger a chave)
private_key = "0xac4bc58836108072d9ae42e4930fbad3626cef8d9e2add14f9a4950ceac87c96"

# Endereço do nó de saída
egress_address = "0xA70a148B4df4E66a056fE2F78d6c8083792bB721"
# Chave privada para assinar a transação (não usar em produção sem proteger a chave)
egress_private_key = "0x6d93f018b02f0e8d6cb7d406bebce58778b0f2e1a1d122350418f47ebfebc4e2"

# Endereço do auditor
auditor_address = "0xA70a148B4df4E66a056fE2F78d6c8083792bB721"
# Chave privada auditor para assinar a transação (não usar em produção sem proteger a chave)
auditor_private_key = "0x6d93f018b02f0e8d6cb7d406bebce58778b0f2e1a1d122350418f47ebfebc4e2"

# Função para chamar `echo` e emitir o evento
def call_echo(message):
    # Prepara a transação para chamar a função `echo`
    transaction = contract.functions.echo(message).build_transaction({
        'from': sender_address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(sender_address),
    })

    # Assina a transação com a chave privada
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)

    # Envia a transação
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)

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

    # Assina a transação com a chave privada
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)

    # Envia a transação
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)

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

    # Assina a transação com a chave privada
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)

    # Envia a transação
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)

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

    # Assina a transação com a chave privada
    signed_transaction = w3.eth.account.sign_transaction(transaction, egress_private_key)

    tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)

    tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
    if tx_receipt:
        if tx_receipt['status'] == 1:
            print("logProbe: A transação foi executada com sucesso.")
        else:
            print("logProbe: A transação falhou.")
    else:
        print("logProbe: A transação ainda está pendente.")

    return w3.to_hex(tx_hash)

def call_getFlowCompliance(flowId):
    # Chamar a função `getFlowCompliance`
    success, fail, nil = contract.functions.getFlowCompliance(flowId).call()    

    return success, fail, nil   

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

    tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
    if tx_receipt:
        if tx_receipt['status'] == 1:
            print("deployFlowContract: A transação foi executada com sucesso.")
        else:
            print("deployFlowContract: A transação falhou.")
    else:
        print("deployFlowContract: A transação ainda está pendente.")

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

    tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
    if tx_receipt:
        if tx_receipt['status'] == 1:
            print("setRefSig: A transação foi executada com sucesso.")
        else:
            print("setRefSig: A transação falhou.")
    else:
        print("setRefSig: A transação ainda está pendente.")

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

# Chamadas pelo Controller
# deployFlowContract(String flowId, String routeId, String edgeAddr)
# Descrição: Implanta o contrato de fluxo associado a uma rota e a um endereço de borda.
# setRefSig(String flowId, String routeId, String timestamp, String lightMultSig)
# Descrição: Define a assinatura de referência para um fluxo e rota específicos, incluindo o timestamp e a assinatura leve múltipla.
# Chamada pelo Egress Edge
# logProbe(String flowId, String routeId, String timestamp, String lightMultSig)
# Descrição: Registra as informações sobre o caminho percorrido pela sonda, incluindo a verificação de conformidade desse trajeto com o caminho previamente definido pelo controller.
