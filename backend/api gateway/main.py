from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from httpx import AsyncClient
import asyncio
import requests
import logging
import traceback
from fastapi.middleware.cors import CORSMiddleware


# configuração do servidor
app = FastAPI()


# configuração de Cross-Origin Resource Sharing (CORS), isto é, poder receber requisições de outros dominios
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# configuração do log
logging.basicConfig(
    filename=r'C:\Users\gabri\OneDrive\Área de Trabalho\frank\projeto final\backend\server.log',
    level=logging.INFO,
    format='GATEWAY %(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)


# retorna ip 0.0.0.0 da nuvem http://SalMolhado.pythonanywhere.com/ip
def get_ip():
    response = requests.get(f"http://SalMolhado.pythonanywhere.com/ip")
    return response.json()['value']


# Pega a lista de serviços do servidor de registro (finder service). Apenas uma vez
async def get_services():
    while True:
        async with AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8001/services")
            service_dict = response.json()
            # Se ao menos dois serviços foram encontrados, retorna a lista de serviços
            if len(service_dict) >= 2:
                return service_dict
            # Caso contrário, aguarda um pouco antes de tentar novamente
            await asyncio.sleep(1)


# não tem problema deixar num python dict pois quaisquer instâncias do gateway terão o mesmo conteúdo
services = {}


# ao iniciar
@app.on_event("startup")
async def startup_event():
    global services
    services = await get_services()


# quando ocorrer uma exceção
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logging.error(f"An error occurred: {str(exc)}")
    logging.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"},
    )


# redirecionar
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    try:
        # Pega o host do serviço da lista de serviços local
        host = services.get(service)
        if host is None:
            raise HTTPException(status_code=404, detail="Service not found")

        url = f"http://{host}/{path}"

        data = None
        if request.method in ["POST", "PUT"] and request.headers.get("Content-Type") == "application/json":
            try:
                data = await request.json()
            except Exception as e:
                # erro no JSON
                logging.error(f"Failed to parse JSON: {e}")
                raise HTTPException(status_code=400, detail="Invalid JSON") from e

        async with AsyncClient() as client:
            if request.method == "GET":
                response = await client.get(url, params=request.query_params)
            elif request.method in ["POST", "PUT"]:
                response = await client.request(request.method, url, json=data, params=request.query_params)
            elif request.method == "DELETE":
                response = await client.delete(url)
            else:
                # erro no método da requisição
                raise HTTPException(status_code=405, detail="Invalid request method")

            # lança execeção se for o caso
            response.raise_for_status()

            # responde com JSON apropriado
            return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        # erro genérico
        logging.exception("An error occurred while processing the request")
        raise HTTPException(status_code=500, detail=str(e)) from e
