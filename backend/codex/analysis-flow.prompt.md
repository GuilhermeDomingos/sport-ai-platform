# analysis-flow.prompt.md — Implementação do Fluxo de Análise Mockada

## Contexto do projeto

Estou criando uma plataforma web chamada inicialmente **Sport AI Platform**.

A plataforma será voltada para análise esportiva por vídeo com IA, começando pelo esporte **Crossfit**.

O backend já possui uma API inicial em **FastAPI** com:

- rota de health check
- upload de vídeos
- validação de vídeos
- salvamento local em `app/uploads`
- retorno de `videoId`
- consulta básica de vídeo salvo

Agora quero evoluir o backend criando o fluxo inicial de análise de vídeo.

IMPORTANTE:

Neste momento, **NÃO implementar IA real**.

O objetivo é apenas criar a estrutura da análise usando dados mockados para simular como será o fluxo real no futuro.

---

## Objetivo desta implementação

Implementar no backend o fluxo:

```txt
1. Usuário envia um vídeo
2. Backend salva o vídeo e retorna videoId
3. Usuário solicita análise do vídeo
4. Backend valida se o vídeo existe
5. Backend retorna uma análise mockada de Crossfit/Squat
6. Usuário pode consultar o resultado da análise pelo videoId
```

---

## Stack atual

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- python-multipart
- Armazenamento local

---

## Regras importantes

### Fazer agora

- Criar estrutura modular para análise
- Criar schemas Pydantic de análise
- Criar service de análise
- Criar routes de análise
- Registrar router no `main.py`
- Validar se o vídeo existe antes de analisar
- Retornar análise mockada
- Retornar erro `404` caso o vídeo não exista
- Manter código simples, legível e fácil de evoluir

### Não fazer agora

Não implementar:

- OpenCV
- MediaPipe
- IA real
- Machine Learning
- banco de dados
- autenticação
- filas
- Celery
- Redis
- RabbitMQ
- Docker
- cloud storage
- websocket
- background jobs reais
- testes automatizados

Esses itens serão feitos em etapas futuras.

---

## Estrutura atual esperada

A estrutura atual do backend deve estar parecida com:

```txt
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── videos.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── video_service.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── video_schema.py
│   └── uploads/
├── requirements.txt
└── README.md
```

---

## Nova estrutura a adicionar

Adicionar os seguintes arquivos:

```txt
backend/
├── app/
│   ├── routes/
│   │   └── analysis.py
│   ├── services/
│   │   └── analysis_service.py
│   └── schemas/
│       └── analysis_schema.py
```

A estrutura final deverá ficar assim:

```txt
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── videos.py
│   │   └── analysis.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── video_service.py
│   │   └── analysis_service.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── video_schema.py
│   │   └── analysis_schema.py
│   └── uploads/
├── requirements.txt
└── README.md
```

---

# Endpoints a implementar

## 1. Solicitar análise de vídeo

```http
POST /videos/{video_id}/analyze
```

### Responsabilidade

Esse endpoint deve:

1. receber o `video_id`
2. validar se existe vídeo salvo com esse `video_id`
3. executar uma análise mockada
4. retornar status `completed`
5. retornar métricas mockadas de Crossfit
6. retornar feedbacks textuais mockados

### Resposta esperada

```json
{
  "videoId": "uuid-do-video",
  "status": "completed",
  "sport": "crossfit",
  "movement": "squat",
  "metrics": {
    "performanceScore": 82,
    "depthScore": 88,
    "kneeStabilityScore": 76,
    "spineAlignmentScore": 80,
    "consistencyScore": 84
  },
  "feedback": [
    "Boa profundidade no agachamento.",
    "Foi detectada leve instabilidade nos joelhos.",
    "A consistência entre as repetições está boa."
  ]
}
```

---

## 2. Consultar resultado da análise

```http
GET /videos/{video_id}/analysis
```

### Responsabilidade

Esse endpoint deve:

1. receber o `video_id`
2. validar se existe vídeo salvo com esse `video_id`
3. retornar a análise mockada do vídeo
4. retornar erro `404` se o vídeo não existir

### Resposta esperada

```json
{
  "videoId": "uuid-do-video",
  "status": "completed",
  "sport": "crossfit",
  "movement": "squat",
  "metrics": {
    "performanceScore": 82,
    "depthScore": 88,
    "kneeStabilityScore": 76,
    "spineAlignmentScore": 80,
    "consistencyScore": 84
  },
  "feedback": [
    "Boa profundidade no agachamento.",
    "Foi detectada leve instabilidade nos joelhos.",
    "A consistência entre as repetições está boa."
  ]
}
```

---

# Implementação passo a passo

---

## Passo 1 — Criar schema de análise

Criar o arquivo:

```txt
app/schemas/analysis_schema.py
```

Conteúdo esperado:

```python
from pydantic import BaseModel


class AnalysisMetrics(BaseModel):
    performanceScore: int
    depthScore: int
    kneeStabilityScore: int
    spineAlignmentScore: int
    consistencyScore: int


class AnalysisResponse(BaseModel):
    videoId: str
    status: str
    sport: str
    movement: str
    metrics: AnalysisMetrics
    feedback: list[str]
```

---

## Passo 2 — Criar service de análise

Criar o arquivo:

```txt
app/services/analysis_service.py
```

Esse arquivo deve conter a regra de negócio da análise.

Conteúdo esperado:

```python
from fastapi import HTTPException

from app.services.video_service import get_video_info


def build_mock_analysis(video_id: str) -> dict:
    return {
        "videoId": video_id,
        "status": "completed",
        "sport": "crossfit",
        "movement": "squat",
        "metrics": {
            "performanceScore": 82,
            "depthScore": 88,
            "kneeStabilityScore": 76,
            "spineAlignmentScore": 80,
            "consistencyScore": 84,
        },
        "feedback": [
            "Boa profundidade no agachamento.",
            "Foi detectada leve instabilidade nos joelhos.",
            "A consistência entre as repetições está boa.",
        ],
    }


def analyze_video(video_id: str) -> dict:
    try:
        get_video_info(video_id)
    except HTTPException as error:
        raise error

    return build_mock_analysis(video_id)


def get_analysis(video_id: str) -> dict:
    try:
        get_video_info(video_id)
    except HTTPException as error:
        raise error

    return build_mock_analysis(video_id)
```

### Observação importante

A função `get_video_info(video_id)` já deve existir em `app/services/video_service.py`.

Ela será usada para validar se o vídeo existe antes de retornar a análise.

Se a função `get_video_info` ainda não existir ou estiver incompleta, implementar/ajustar ela para lançar `HTTPException(status_code=404)` quando o vídeo não for encontrado.

---

## Passo 3 — Criar routes de análise

Criar o arquivo:

```txt
app/routes/analysis.py
```

Conteúdo esperado:

```python
from fastapi import APIRouter

from app.schemas.analysis_schema import AnalysisResponse
from app.services.analysis_service import analyze_video, get_analysis

router = APIRouter()


@router.post("/{video_id}/analyze", response_model=AnalysisResponse)
def analyze(video_id: str):
    return analyze_video(video_id)


@router.get("/{video_id}/analysis", response_model=AnalysisResponse)
def get_analysis_result(video_id: str):
    return get_analysis(video_id)
```

---

## Passo 4 — Registrar router no main.py

Abrir o arquivo:

```txt
app/main.py
```

Adicionar o import:

```python
from app.routes.analysis import router as analysis_router
```

Registrar o router:

```python
app.include_router(
    analysis_router,
    prefix="/videos",
    tags=["Analysis"]
)
```

O arquivo `app/main.py` deve ficar com comportamento equivalente a:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.videos import router as videos_router
from app.routes.analysis import router as analysis_router

app = FastAPI(
    title="Sport AI API",
    description="API para upload e análise de vídeos esportivos",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(videos_router, prefix="/videos", tags=["Videos"])
app.include_router(analysis_router, prefix="/videos", tags=["Analysis"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

---

## Passo 5 — Validar service de vídeo

Abrir o arquivo:

```txt
app/services/video_service.py
```

Garantir que exista uma função parecida com:

```python
from fastapi import HTTPException
from app.core.config import UPLOAD_DIR


def get_video_info(video_id: str) -> dict:
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.stem == video_id:
            return {
                "videoId": video_id,
                "filename": file_path.name,
                "exists": True,
                "path": str(file_path),
            }

    raise HTTPException(
        status_code=404,
        detail="Vídeo não encontrado."
    )
```

### Regras dessa função

- procurar arquivos dentro de `UPLOAD_DIR`
- comparar `file_path.stem` com `video_id`
- se encontrar, retornar informações do vídeo
- se não encontrar, retornar `404`

---

# Fluxo de teste manual

## 1. Rodar API

Na pasta `backend`, executar:

```bash
python -m uvicorn app.main:app --reload
```

A API deve subir em:

```txt
http://localhost:8000
```

---

## 2. Testar health check

Abrir:

```txt
http://localhost:8000/health
```

Resposta esperada:

```json
{
  "status": "ok"
}
```

---

## 3. Abrir Swagger

Abrir:

```txt
http://localhost:8000/docs
```

---

## 4. Enviar vídeo

Usar o endpoint:

```http
POST /videos/upload
```

Selecionar um vídeo válido.

Copiar o campo retornado:

```txt
videoId
```

---

## 5. Solicitar análise

Usar o endpoint:

```http
POST /videos/{video_id}/analyze
```

Substituir `{video_id}` pelo ID retornado no upload.

Resposta esperada:

```json
{
  "videoId": "uuid-do-video",
  "status": "completed",
  "sport": "crossfit",
  "movement": "squat",
  "metrics": {
    "performanceScore": 82,
    "depthScore": 88,
    "kneeStabilityScore": 76,
    "spineAlignmentScore": 80,
    "consistencyScore": 84
  },
  "feedback": [
    "Boa profundidade no agachamento.",
    "Foi detectada leve instabilidade nos joelhos.",
    "A consistência entre as repetições está boa."
  ]
}
```

---

## 6. Consultar análise

Usar o endpoint:

```http
GET /videos/{video_id}/analysis
```

Resposta esperada:

```json
{
  "videoId": "uuid-do-video",
  "status": "completed",
  "sport": "crossfit",
  "movement": "squat",
  "metrics": {
    "performanceScore": 82,
    "depthScore": 88,
    "kneeStabilityScore": 76,
    "spineAlignmentScore": 80,
    "consistencyScore": 84
  },
  "feedback": [
    "Boa profundidade no agachamento.",
    "Foi detectada leve instabilidade nos joelhos.",
    "A consistência entre as repetições está boa."
  ]
}
```

---

## 7. Testar vídeo inexistente

Usar um ID fake:

```http
POST /videos/id-inexistente/analyze
```

Resposta esperada:

```json
{
  "detail": "Vídeo não encontrado."
}
```

Status esperado:

```txt
404
```

---

# Testes via cURL

## Solicitar análise

```bash
curl -X POST "http://localhost:8000/videos/SEU_VIDEO_ID/analyze"
```

## Consultar análise

```bash
curl -X GET "http://localhost:8000/videos/SEU_VIDEO_ID/analysis"
```

---

# Critérios de aceite

A implementação estará pronta quando:

- API subir sem erro
- `/health` continuar funcionando
- Swagger abrir normalmente
- endpoint `POST /videos/{video_id}/analyze` aparecer no Swagger
- endpoint `GET /videos/{video_id}/analysis` aparecer no Swagger
- análise validar se o vídeo existe
- análise retornar `404` para vídeo inexistente
- análise retornar métricas mockadas para vídeo existente
- análise retornar feedbacks textuais
- código estiver separado em:
  - `schemas/analysis_schema.py`
  - `services/analysis_service.py`
  - `routes/analysis.py`
- `main.py` registrar o router de análise corretamente

---

# Resultado esperado após essa etapa

Após essa implementação, o backend estará preparado para o seguinte fluxo:

```txt
Upload do vídeo
→ retorno do videoId
→ solicitação de análise
→ retorno de métricas mockadas
→ consulta futura do resultado
```

Esse fluxo servirá como base para substituir os dados mockados por análise real usando OpenCV e MediaPipe nas próximas etapas.
