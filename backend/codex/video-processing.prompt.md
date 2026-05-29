# video-processing.prompt.md — Implementação do Processamento Inicial de Vídeo

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
- fluxo de análise mockada com métricas fake para Crossfit/Squat

Agora quero evoluir o backend criando a primeira etapa de processamento real do vídeo.

IMPORTANTE:

Neste momento, **NÃO implementar análise biomecânica real**.

O objetivo desta etapa é apenas:

- abrir o vídeo salvo
- validar se o arquivo pode ser lido
- extrair metadados reais do vídeo
- retornar informações técnicas do arquivo

---

## Objetivo desta implementação

Implementar no backend um serviço de processamento inicial de vídeo.

O fluxo esperado será:

```txt
1. Usuário envia um vídeo
2. Backend salva o vídeo e retorna videoId
3. Usuário solicita processamento do vídeo
4. Backend localiza o arquivo salvo
5. Backend abre o vídeo com OpenCV
6. Backend extrai metadados reais
7. Backend retorna os dados processados
```

---

## Stack atual

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- python-multipart
- OpenCV
- Armazenamento local

---

## Dependência nova

Adicionar no `requirements.txt`:

```txt
opencv-python
```

Depois instalar:

```bash
pip install -r requirements.txt
```

Ou, se preferir instalar direto:

```bash
pip install opencv-python
```

---

## Regras importantes

### Fazer agora

- Criar estrutura modular para processamento de vídeo
- Criar schema Pydantic de processamento
- Criar service de processamento
- Criar route de processamento
- Registrar router no `main.py`
- Validar se o vídeo existe antes de processar
- Abrir o vídeo com OpenCV
- Extrair metadados reais
- Retornar erro `404` caso o vídeo não exista
- Retornar erro `400` caso o vídeo não consiga ser aberto/lido
- Manter código simples, legível e fácil de evoluir

### Não fazer agora

Não implementar:

- MediaPipe
- Pose estimation
- IA real
- Machine Learning
- análise biomecânica real
- detecção de squat
- cálculo de ângulo corporal
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

## Nova estrutura a adicionar

Adicionar os seguintes arquivos:

```txt
backend/
├── app/
│   ├── routes/
│   │   └── processing.py
│   ├── services/
│   │   └── video_processing_service.py
│   └── schemas/
│       └── processing_schema.py
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
│   │   ├── analysis.py
│   │   └── processing.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── video_service.py
│   │   ├── analysis_service.py
│   │   └── video_processing_service.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── video_schema.py
│   │   ├── analysis_schema.py
│   │   └── processing_schema.py
│   └── uploads/
├── requirements.txt
└── README.md
```

---

# Endpoint a implementar

## Processar vídeo

```http
POST /videos/{video_id}/process
```

### Responsabilidade

Esse endpoint deve:

1. receber o `video_id`
2. validar se existe vídeo salvo com esse `video_id`
3. abrir o vídeo com OpenCV
4. extrair metadados técnicos
5. retornar status `processed`
6. retornar metadados reais do vídeo

### Resposta esperada

```json
{
  "videoId": "uuid-do-video",
  "status": "processed",
  "metadata": {
    "durationSeconds": 18.4,
    "fps": 30.0,
    "totalFrames": 552,
    "resolution": {
      "width": 1920,
      "height": 1080
    },
    "fileSizeMb": 24.8
  }
}
```

---

# Metadados que devem ser extraídos

O OpenCV deve extrair:

- FPS
- total de frames
- largura do vídeo
- altura do vídeo
- duração em segundos

O Python deve extrair:

- tamanho do arquivo em MB

---

# Implementação passo a passo

---

## Passo 1 — Atualizar requirements.txt

Abrir:

```txt
requirements.txt
```

Adicionar:

```txt
opencv-python
```

O arquivo deve ficar parecido com:

```txt
fastapi
uvicorn
python-multipart
opencv-python
```

---

## Passo 2 — Criar schema de processamento

Criar o arquivo:

```txt
app/schemas/processing_schema.py
```

Conteúdo esperado:

```python
from pydantic import BaseModel


class VideoResolution(BaseModel):
    width: int
    height: int


class VideoMetadata(BaseModel):
    durationSeconds: float
    fps: float
    totalFrames: int
    resolution: VideoResolution
    fileSizeMb: float


class VideoProcessingResponse(BaseModel):
    videoId: str
    status: str
    metadata: VideoMetadata
```

---

## Passo 3 — Criar service de processamento

Criar o arquivo:

```txt
app/services/video_processing_service.py
```

Esse arquivo deve conter a regra de negócio de processamento.

Conteúdo esperado:

```python
from pathlib import Path

import cv2
from fastapi import HTTPException

from app.services.video_service import get_video_info


def process_video(video_id: str) -> dict:
    video_info = get_video_info(video_id)
    video_path = Path(video_info["path"])

    if not video_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Vídeo não encontrado."
        )

    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        raise HTTPException(
            status_code=400,
            detail="Não foi possível abrir o vídeo para processamento."
        )

    fps = capture.get(cv2.CAP_PROP_FPS)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    capture.release()

    if fps <= 0:
        duration_seconds = 0
    else:
        duration_seconds = total_frames / fps

    file_size_mb = video_path.stat().st_size / (1024 * 1024)

    return {
        "videoId": video_id,
        "status": "processed",
        "metadata": {
            "durationSeconds": round(duration_seconds, 2),
            "fps": round(fps, 2),
            "totalFrames": total_frames,
            "resolution": {
                "width": width,
                "height": height,
            },
            "fileSizeMb": round(file_size_mb, 2),
        },
    }
```

---

## Passo 4 — Criar route de processamento

Criar o arquivo:

```txt
app/routes/processing.py
```

Conteúdo esperado:

```python
from fastapi import APIRouter

from app.schemas.processing_schema import VideoProcessingResponse
from app.services.video_processing_service import process_video

router = APIRouter()


@router.post("/{video_id}/process", response_model=VideoProcessingResponse)
def process(video_id: str):
    return process_video(video_id)
```

---

## Passo 5 — Registrar router no main.py

Abrir o arquivo:

```txt
app/main.py
```

Adicionar o import:

```python
from app.routes.processing import router as processing_router
```

Registrar o router:

```python
app.include_router(
    processing_router,
    prefix="/videos",
    tags=["Processing"]
)
```

O arquivo `app/main.py` deve ficar com comportamento equivalente a:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.videos import router as videos_router
from app.routes.analysis import router as analysis_router
from app.routes.processing import router as processing_router

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
app.include_router(processing_router, prefix="/videos", tags=["Processing"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

---

# Fluxo de teste manual

## 1. Instalar dependências

Na pasta `backend`, com o ambiente virtual ativo:

```bash
pip install -r requirements.txt
```

---

## 2. Rodar API

Na pasta `backend`, executar:

```bash
python -m uvicorn app.main:app --reload
```

A API deve subir em:

```txt
http://localhost:8000
```

---

## 3. Testar health check

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

## 4. Abrir Swagger

Abrir:

```txt
http://localhost:8000/docs
```

---

## 5. Enviar vídeo

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

## 6. Processar vídeo

Usar o endpoint:

```http
POST /videos/{video_id}/process
```

Substituir `{video_id}` pelo ID retornado no upload.

Resposta esperada:

```json
{
  "videoId": "uuid-do-video",
  "status": "processed",
  "metadata": {
    "durationSeconds": 18.4,
    "fps": 30.0,
    "totalFrames": 552,
    "resolution": {
      "width": 1920,
      "height": 1080
    },
    "fileSizeMb": 24.8
  }
}
```

---

## 7. Testar vídeo inexistente

Usar um ID fake:

```http
POST /videos/id-inexistente/process
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

## Processar vídeo

```bash
curl -X POST "http://localhost:8000/videos/SEU_VIDEO_ID/process"
```

---

# Critérios de aceite

A implementação estará pronta quando:

- API subir sem erro
- `/health` continuar funcionando
- Swagger abrir normalmente
- endpoint `POST /videos/{video_id}/process` aparecer no Swagger
- endpoint validar se o vídeo existe
- endpoint retornar `404` para vídeo inexistente
- endpoint abrir vídeo com OpenCV
- endpoint retornar FPS
- endpoint retornar total de frames
- endpoint retornar duração em segundos
- endpoint retornar resolução
- endpoint retornar tamanho do arquivo em MB
- código estiver separado em:
  - `schemas/processing_schema.py`
  - `services/video_processing_service.py`
  - `routes/processing.py`
- `main.py` registrar o router de processamento corretamente

---

# Resultado esperado após essa etapa

Após essa implementação, o backend estará preparado para o seguinte fluxo:

```txt
Upload do vídeo
→ retorno do videoId
→ processamento do vídeo
→ extração de metadados reais
→ retorno dos dados técnicos
```

Esse fluxo servirá como base para as próximas etapas:

```txt
Extração de frames
→ detecção de pose
→ cálculo de métricas biomecânicas
→ análise real de Crossfit/Squat
```
