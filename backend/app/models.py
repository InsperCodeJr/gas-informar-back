# models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum
from datetime import datetime
import enum
from .database import Base
from sqlalchemy import JSON

# Tipo de exercício
class ExerciseTypeEnum(str, enum.Enum):
    text = "text"
    multiple_choice = "multiple_choice"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    username = Column(String(200), unique=True, index=True, nullable=False)
    role = Column(String(50), nullable=False, default="aluno")
    senha_hash = Column(String(300), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    turma = Column(String(64), nullable=True, index=True) # category/turma (Python, WebDev)

    aulas = relationship("Aula", back_populates="autor", cascade="all, delete-orphan")
    respostas = relationship("RespostaAluno", back_populates="aluno", cascade="all, delete-orphan")
    tentativas = relationship("TentativaAula", back_populates="aluno", cascade="all, delete-orphan")

class Aula(Base):
    __tablename__ = "aulas"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    autor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    category = Column(String(64), nullable=True, index=True) # category/turma (Python, WebDev)
    # Aulas em revisão ficam visíveis somente para admins/professores.
    # default=True preserva compatibilidade com bancos existentes; novas aulas
    # criadas pelo frontend são enviadas explicitamente como rascunho.
    publicada = Column(Boolean, nullable=False, default=True, index=True)

    autor = relationship("User", back_populates="aulas")
    blocos = relationship("ConteudoBloco", back_populates="aula", cascade="all, delete-orphan", order_by="ConteudoBloco.ordem")
    exercicios = relationship("Exercicio", back_populates="aula", cascade="all, delete-orphan", order_by="Exercicio.ordem")
    tentativas = relationship("TentativaAula", back_populates="aula", cascade="all, delete-orphan")

class ConteudoBloco(Base):
    __tablename__ = "conteudo_blocos"
    id = Column(Integer, primary_key=True, index=True)
    aula_id = Column(Integer, ForeignKey("aulas.id", ondelete="CASCADE"))
    titulo = Column(String(200), nullable=True)
    texto = Column(Text, nullable=True)
    ordem = Column(Integer, default=0)
    imagem_url = Column(String(1024), nullable=True)
    # youtube_url = Column(String(512), nullable=True)

    aula = relationship("Aula", back_populates="blocos")

# models.py (classe Exercicio)

class Exercicio(Base):
    __tablename__ = "exercicios"
    id = Column(Integer, primary_key=True, index=True)
    aula_id = Column(Integer, ForeignKey("aulas.id", ondelete="CASCADE"))
    titulo = Column(String(200), nullable=True)
    enunciado = Column(Text, nullable=False)
    tipo = Column(SQLEnum(ExerciseTypeEnum), nullable=False, default=ExerciseTypeEnum.text)
    resposta_modelo = Column(Text, nullable=True)
    pontos = Column(Integer, default=1)
    ordem = Column(Integer, default=0)

    # NOVO: feedback geral do professor para a questão (visível a todos os alunos)
    feedback_professor = Column(Text, nullable=True)

    # armazenar alternativas como JSONB:
    alternativas = Column(JSON, nullable=True, default=list)
    correct_alternativas = Column(JSON, nullable=True, default=list)

    aula = relationship("Aula", back_populates="exercicios")
    alternativas_rel = relationship("Alternativa", back_populates="exercicio", cascade="all, delete-orphan", order_by="Alternativa.id")
    respostas = relationship("RespostaAluno", back_populates="exercicio", cascade="all, delete-orphan")

class Alternativa(Base):
    """
    Modelo legacy — mantido apenas caso você tenha migrações antigas que criaram essa tabela.
    Novas rotas não gravam mais nessa tabela quando opção JSONB estiver ativa.
    """
    __tablename__ = "alternativas"
    id = Column(Integer, primary_key=True, index=True)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id", ondelete="CASCADE"))
    texto = Column(Text, nullable=False)

    exercicio = relationship("Exercicio", back_populates="alternativas_rel")

class TentativaAula(Base):
    __tablename__ = "tentativas_aula"
    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    aula_id = Column(Integer, ForeignKey("aulas.id", ondelete="CASCADE"))
    finalizada = Column(Boolean, default=False)
    pontuacao = Column(Integer, default=0, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    finalized_at = Column(DateTime, nullable=True)

    aluno = relationship("User", back_populates="tentativas")
    aula = relationship("Aula", back_populates="tentativas")
    respostas = relationship("RespostaAluno", back_populates="tentativa", cascade="all, delete-orphan")


class RespostaAluno(Base):
    __tablename__ = "respostas_aluno"
    id = Column(Integer, primary_key=True, index=True)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id", ondelete="CASCADE"))
    aluno_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    enviado_em = Column(DateTime, default=datetime.utcnow)
    resposta_texto = Column(Text, nullable=True)
    alternativa_id = Column(Integer, nullable=True)
    pontuacao = Column(Integer, default=0)
    tentativa_id = Column(Integer, ForeignKey("tentativas_aula.id", ondelete="CASCADE"), nullable=True)
    feedback_professor = Column(Text, nullable=True)

    exercicio = relationship("Exercicio", back_populates="respostas")
    aluno = relationship("User", back_populates="respostas")
    tentativa = relationship("TentativaAula", back_populates="respostas")
