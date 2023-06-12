from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Integer, create_engine, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from datetime import datetime
import requests
import logging

# configuração do log
logging.basicConfig(
    filename=r'C:\Users\gabri\OneDrive\Área de Trabalho\frank\projeto final\backend\server.log',
    level=logging.INFO,
    format='LOGGING %(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)


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
    # if response.status_code == 200:
    # print("Service registered successfully")
    # else:
    # print("Failed to register service", response.content)


# realiza o registro
register_service('logging', ':8002')

# configuração da base de dados SQLite
DATABASE_URL = "sqlite:///./log.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# tabela com os registros
class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    temperature = Column(String)
    trigger_activated = Column(Boolean)


# finaliza setup da base de dados
Base.metadata.create_all(bind=engine)

# configuração do servidor
app = FastAPI()


# dados de entrada
class SensorDataIn(BaseModel):
    temperature: str
    trigger_activated: bool


# dados de saida
class SensorDataOut(SensorDataIn):
    id: int
    timestamp: datetime

    # permite conversão a partir de uma linha da tabela sensor_data
    class Config:
        orm_mode = True


# abre conexão com base de dados quando necessário
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# registra informações após receber e após responder uma requisição
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"Incoming request: {request.method} {request.url}")
    # passa para a rota, já que não tem outros middlewares
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response


# registra na tabela sensor_data
@app.post("/data", response_model=SensorDataOut, status_code=201)
async def log_data(sensor_data_in: SensorDataIn, db: Session = Depends(get_db)):
    sensor_data = SensorData(**sensor_data_in.dict())
    db.add(sensor_data)
    db.commit()
    db.refresh(sensor_data)
    return sensor_data


# retorna todas as linhas da tabela sensor_data
@app.get("/data", response_model=List[SensorDataOut])
async def get_data(db: Session = Depends(get_db)):
    sensor_data = db.query(SensorData).all()
    return [SensorDataOut.from_orm(item) for item in sensor_data]
