# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

from .routers import users, aulas, uploads
from . import models
from .database import engine
import os

app = FastAPI(title="GAS Informar - API")

# Configuração de CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Garante as tabelas em instalações novas.
models.Base.metadata.create_all(bind=engine)


def ensure_aula_publicada_column():
    """Migração leve para instalações existentes, sem exigir Alembic.

    A coluna nova nasce como TRUE para não esconder aulas que já estavam em produção.
    Novas aulas criadas pela interface são enviadas explicitamente como rascunho.
    """
    inspector = inspect(engine)
    if "aulas" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("aulas")}
    if "publicada" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE aulas ADD COLUMN publicada BOOLEAN NOT NULL DEFAULT TRUE"))


ensure_aula_publicada_column()

# Ensure static/upload dir exists (para armazenar imagens)
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# monta static (serve /static/...)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inclui os routers da aplicação (ordem não crítica)
app.include_router(users.router)
app.include_router(aulas.router)
app.include_router(uploads.router)


@app.get("/")
def root():
    return {"msg": "API do GAS Informar rodando com sucesso!"}
