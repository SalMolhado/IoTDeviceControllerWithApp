from fastapi import FastAPI, Request
import requests
import logging
from redis import Redis
from types import SimpleNamespace


# configuração do log
logging.basicConfig(
    filename=r'C:\Users\gabri\OneDrive\Área de Trabalho\frank\projeto final\backend\server.log',
    level=logging.INFO,
    format='CONTROL %(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)

# configuração da base de dados SQLite
DATABASE_URL = "redis://localhost:6379"


# retorna ip 0.0.0.0 da nuvem http://SalMolhado.pythonanywhere.com/ip
def get_ip():
    response = requests.get(f"http://SalMolhado.pythonanywhere.com/ip")
    return response.json()['value']


# se registra no Service Finder
def register_service(service_name, service_port):
    payload = {
        'service_name': service_name,
        'service_address': get_ip() + service_port,
    }
    response = requests.post(f'http://127.0.0.1:8001/register', json=payload)
    if response.status_code == 200:
        print("Service registered successfully")
    else:
        print("Failed to register service", response.status_code)


register_service('control', ':8003')

# configuração do servidor
app = FastAPI()
app.state = SimpleNamespace()


# ao iniciar
@app.on_event("startup")
async def startup():
    app.state.redis = Redis.from_url(DATABASE_URL, decode_responses=True)
    # set default values if they don't exist
    if not app.state.redis.get('condition'):
        app.state.redis.set('condition', 40.0)
    if not app.state.redis.get('angle'):
        app.state.redis.set('angle', 180)


# desconecta-se da base de dados
@app.on_event("shutdown")
async def shutdown():
    app.state.redis.close()


# registra informações após receber e após responder uma requisição
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Response: {response.status_code}")
    return response


# atualiza temperatura minima registrada pelo sensor para ativar o atuador
@app.post("/condition/{new_value}", status_code=201)
async def update_condition(new_value: float):
    app.state.redis.set('condition', new_value)
    return {"status": "updated", "new_value": new_value}


# atualiza angulo ao qual a hélice do atuador rotaciona
@app.post("/angle/{new_value}", status_code=201)
async def update_angle(new_value: int):
    app.state.redis.set('angle', new_value)
    return {"status": "updated", "new_value": new_value}


# retorna temperatura minima registrada pelo sensor para ativar o atuador
@app.get("/condition")
async def get_condition():
    condition = app.state.redis.get('condition')
    return float(condition) if condition else None


# retorna angulo ao qual a hélice do atuador rotaciona
@app.get("/angle")
async def get_angle():
    angle = app.state.redis.get('angle')
    return int(angle) if angle else None
