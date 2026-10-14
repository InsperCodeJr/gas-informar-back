 # schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
import re

# ---------- usuários ----------
class UserBase(BaseModel):
    nome: str
    username: str
    role: str  # 'admin' | 'professor' | 'aluno'
    turma: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 4:
            raise ValueError('Username deve ter no mínimo 4 caracteres')
        digit_count = sum(c.isdigit() for c in v)
        if digit_count < 2:
            raise ValueError('Username deve conter pelo menos 2 dígitos')
        return v

class UserCreate(UserBase):
    senha: str

class UserOut(UserBase):
    id: int

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
    senha: Optional[str] = None
    turma: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) < 4:
                raise ValueError('Username deve ter no mínimo 4 caracteres')
            digit_count = sum(c.isdigit() for c in v)
            if digit_count < 2:
                raise ValueError('Username deve conter pelo menos 2 dígitos')
        return v

    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ---------- aulas / conteúdo / exercícios ----------
class ConteudoBlocoCreate(BaseModel):
    id: Optional[int] = None
    titulo: Optional[str] = None
    texto: Optional[str] = None
    ordem: Optional[int] = None
    imagem_url: Optional[str] = None
    # youtube_url: Optional[str] = None

class ConteudoBlocoOut(ConteudoBlocoCreate):
    id: int

    model_config = {"from_attributes": True}

class ExerciseType(str, Enum):
    text = "text"
    multiple_choice = "multiple_choice"

class AlternativaInOut(BaseModel):
    id: Optional[int] = None
    texto: str
    is_correta: Optional[bool] = None
    model_config = {"from_attributes": True}

class ExercicioCreate(BaseModel):
    id: Optional[int] = None
    titulo: Optional[str] = None
    enunciado: str
    tipo: ExerciseType
    resposta_modelo: Optional[str] = None
    pontos: Optional[int] = 1
    ordem: Optional[int] = 0
    alternativas: Optional[List[AlternativaInOut]] = None
    alternativas_certas: Optional[List[int]] = None
    feedback_professor: Optional[str] = None   # NOVO


class ExercicioOut(BaseModel):
    id: int
    titulo: Optional[str] = None
    enunciado: str
    tipo: ExerciseType
    resposta_modelo: Optional[str] = None
    pontos: int
    ordem: Optional[int] = 0
    alternativas: List[AlternativaInOut] = Field(default_factory=list)
    correct_alternativas: List[int] = Field(default_factory=list)
    feedback_professor: Optional[str] = None

    model_config = {"from_attributes": True}

class AulaCreate(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    blocos: Optional[List[ConteudoBlocoCreate]] = None
    exercicios: Optional[List[ExercicioCreate]] = None
    category: Optional[str] = None
    publicada: bool = False

class AulaOut(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    autor_id: int
    autor_nome: Optional[str] = None
    blocos: List[ConteudoBlocoOut] = Field(default_factory=list)
    exercicios: List[ExercicioOut] = Field(default_factory=list)
    created_at: datetime
    category: Optional[str] = None
    publicada: bool = True
    
    model_config = {"from_attributes": True}

class AulaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    blocos: Optional[List[ConteudoBlocoCreate]] = None
    exercicios: Optional[List[ExercicioCreate]] = None
    category: Optional[str] = None
    publicada: Optional[bool] = None

    model_config = {"from_attributes": True}

# ---------- respostas ----------
class RespostaCreate(BaseModel):
    exercicio_id: int
    resposta_texto: Optional[str] = None
    # alternativa_id refere-se ao id interno do objeto armazenado em Exercicio.alternativas
    alternativa_id: Optional[int] = None

class RespostaOut(BaseModel):
    id: int
    exercicio_id: int
    aluno_id: int
    enviado_em: datetime
    resposta_texto: Optional[str] = None
    alternativa_id: Optional[int] = None
    pontuacao: int
    tentativa_id: Optional[int] = None
    feedback_professor: Optional[str] = None   # opcional (mantém compatibilidade)

    model_config = {"from_attributes": True}

# ---------- Desempenho / relatórios ----------
class QuestaoDesempenho(BaseModel):
    exercicio_id: int
    enunciado: str
    total_respondentes: int
    total_acertos: int
    taxa_acerto: float  # 0..100
    distribuicao_respostas: Optional[Dict[str, int]] = None

class AlunoResumoDesempenho(BaseModel):
    aluno_id: int
    nome: str
    username: str
    turma: Optional[str] = None
    finalizada: bool
    pontuacao_total: float
    percentual_nota: float
    respostas: int
    total_questoes: int
    percentual_questoes: float

class AulaDesempenho(BaseModel):
    aula_id: int
    titulo: str
    category: Optional[str] = None
    pontuacao_maxima: float
    total_alunos: int
    iniciaram: int
    respondentes: int
    media_pontuacao: float
    media_percentual: float
    percentual_conclusao: float  # 0..100
    questoes: List[QuestaoDesempenho] = Field(default_factory=list)
    alunos: List[AlunoResumoDesempenho] = Field(default_factory=list)

class DetalheAlunoResposta(BaseModel):
    exercicio_id: int
    enunciado: str
    resposta_aluno: Optional[str] = None
    alternativa_escolhida_id: Optional[int] = None
    acertou: bool
    pontuacao_obtida: int

class DesempenhoAluno(BaseModel):
    aluno_id: int
    nome: str
    pontuacao_total: int
    finalizada: bool
    responses: List[DetalheAlunoResposta] = Field(default_factory=list)

class FinalizarResponse(BaseModel):
    status: str
    pontuacao: int
