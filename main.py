from flask import Flask, jsonify, request
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

infos = []

@app.route('/')
def home():
    return jsonify("Working")

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
