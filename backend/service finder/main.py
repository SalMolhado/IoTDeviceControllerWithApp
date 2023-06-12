from flask import Flask, request
import requests
import logging
import wmi
from os import getcwd, path


# configuração do log
logging.basicConfig(
    filename=path.join(getcwd(), 'server.log'),
    level=logging.INFO,
    format='FINDER %(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)


# configuração do servidor
app = Flask(__name__)
services = {}  # aonde os serviços ficam armazenados, {"nome serviço": "ip:porta", ...}


# logo após receber uma requisição
@app.before_request
def log_request_info():
    logging.info(f'Headers: {request.headers}')
    logging.info(f'Body: {request.get_data()}')


# logo após responder uma requisição
@app.after_request
def log_response_info(response):
    logging.info(f'Response status: {response.status}')
    return response


# pega ipv4 do Adaptador de Rede sem Fio Wi-Fi
def get_wifi_ipv4_address():
    c = wmi.WMI()
    network_interfaces = c.Win32_NetworkAdapterConfiguration(IPEnabled=True)
    wifi_ipv4_address = network_interfaces[0].IPAddress[0]
    return wifi_ipv4_address


# envia o ip local para api em nuvem aonde outros serviços podem ver em http://SalMolhado.pythonanywhere.com/ip
def post_ip():
    value = get_wifi_ipv4_address()
    url = f"http://SalMolhado.pythonanywhere.com/ip/{value}"
    response = requests.post(url)
    if response.status_code == 200:
        logging.info(f'[[ IMPORTANT ]] POST current ip to pythonanywhere successful')
    else:
        logging.info(f'[[ IMPORTANT ]] POST current ip to pythonanywhere failed')


# atualiza o ip 0.0.0.0 para a API em nuvem
post_ip()


# registra serviços e seus endereços correspondentes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    logging.info(data)
    service_name = data.get('service_name')
    service_address = data.get('service_address')

    if not service_name or not service_address:
        return {"error": "Service name or address missing"}, 400

    services[service_name] = service_address
    # print(f'{service_name}: {service_address}')
    return {"status": "Service registered"}


# devolve serviços registrados
@app.route('/services', methods=['GET'])
def list_services():
    # print('Gateway requested for the current services')
    return services
