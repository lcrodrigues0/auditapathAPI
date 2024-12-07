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

# Substitua pelo endereço do seu contrato
contract_address = '0xBE798e0F0f8a3eea246eDAB36Fcd7ff43C712F75'

# ABI do contrato (cole aqui o ABI do Remix)
abi = [
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
	}
]

# Obter instância do contrato
contract = w3.eth.contract(address=contract_address, abi=abi)
# Endereço da conta que vai enviar a transação (substitua pelo seu endereço)
sender_address = "0xc72DEC353222ae87a3863356c4D07A1FaE64B89c"
# Chave privada para assinar a transação (não use em produção sem proteger a chave!)
private_key = "0x537a710174774a43d072790353b50106b483a69f1969db337d83b8b85a9ee6b9"

# Função para chamar `echo` e emitir o evento
def call_echo(message):
    # Prepare a transação para chamar a função `echo`
    transaction = contract.functions.echo(message).build_transaction({
        'from': sender_address,
        'gas': 2000000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(sender_address),
    })

    # Assine a transação com a chave privada
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)

    # Envie a transação
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)

    return w3.to_hex(tx_hash)

infos = []

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

    infos.append(newFlowContract)

    return jsonify(newFlowContract), 201

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

    infos.append(newRefSig)

    return jsonify(newRefSig), 201

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

    infos.append(newlogProbe)

    return jsonify(newlogProbe), 201



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
