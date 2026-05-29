# frame-extraction.prompt.md — Implementação da Extração de Frames do Vídeo

## Contexto do projeto

Estou criando uma plataforma web chamada inicialmente **Sport AI Platform**.

A plataforma será voltada para análise esportiva por vídeo com IA, começando pelo esporte **Crossfit**.

O backend já possui uma API em **FastAPI** com:

- rota de health check
- upload de vídeos
- validação de vídeos
- salvamento local em `app/uploads`
- retorno de `videoId`
- consulta básica de vídeo salvo
- análise mockada de Crossfit/Squat
- processamento inicial com OpenCV
- extração de metadados reais do vídeo, como FPS, duração, resolução e total de frames

Agora quero evoluir o backend criando a etapa de **extração de frames**.

IMPORTANTE:

Neste momento, **NÃO implementar MediaPipe, IA real ou análise biomecânica**.

O objetivo desta etapa é apenas:

- abrir o vídeo salvo
- extrair imagens/frames em intervalos definidos
- salvar esses frames localmente
- retornar informações sobre os frames extraídos

---

## Objetivo desta implementação

Implementar no backend um serviço de extração de frames do vídeo.

O fluxo esperado será:

```txt
1. Usuário envia um vídeo
2. Backend salva o vídeo e retorna videoId
3. Usuário solicita extração de frames
4. Backend localiza o arquivo salvo
5. Backend abre o vídeo com OpenCV
6. Backend extrai frames em intervalos definidos
7. Backend salva os frames em uma pasta específica
8. Backend retorna os dados da extração
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

## Regras importantes

### Fazer agora

- Criar estrutura modular para extração de frames
- Criar schema Pydantic para resposta da extração
- Criar service de extração de frames
- Criar route de extração de frames
- Registrar router no `main.py`
- Validar se o vídeo existe antes de extrair frames
- Abrir o vídeo com OpenCV
- Extrair frames em intervalo de tempo configurável
- Salvar frames localmente
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

## Nova estrutura a adicionar

Adicionar os seguintes arquivos:

```txt
backend/
├── app/
│   ├── routes/
│   │   └── frames.py
│   ├── services/
│   │   └── frame_extraction_service.py
│   └── schemas/
│       └── frame_schema.py
```

Criar também a pasta de saída para frames:

```txt
backend/
├── app/
│   └── outputs/
```

---

# Endpoint a implementar

## Extrair frames do vídeo

```http
POST /videos/{video_id}/frames/extract
```

### Query parameter opcional

```txt
interval_seconds
```

Valor padrão:

```txt
0.5
```

Exemplo:

```http
POST /videos/{video_id}/frames/extract?interval_seconds=0.5
```

---

# Exemplo de resposta esperada

```json
{
  "videoId": "uuid-do-video",
  "status": "frames_extracted",
  "frameIntervalSeconds": 0.5,
  "totalFramesExtracted": 25,
  "outputDir": "app/outputs/uuid-do-video/frames",
  "frames": [
    "frame_000001.jpg",
    "frame_000002.jpg",
    "frame_000003.jpg"
  ]
}
```

---

# Regras de extração

## Intervalo padrão

Por padrão, extrair:

```txt
1 frame a cada 0.5 segundos
```

## Validação do intervalo

Se `interval_seconds <= 0`, retornar erro `400`.

Mensagem sugerida:

```json
{
  "detail": "O intervalo de extração deve ser maior que zero."
}
```

## Diretório de saída

Salvar frames em:

```txt
app/outputs/{video_id}/frames
```

## Nome dos arquivos

Salvar frames no formato:

```txt
frame_000001.jpg
frame_000002.jpg
frame_000003.jpg
```

## Reprocessamento

Se o endpoint for chamado novamente para o mesmo `video_id`:

- limpar a pasta de frames antes de extrair novamente
- gerar uma nova lista limpa de frames

---

# Implementação passo a passo

## Passo 1 — Atualizar config.py

Abrir:

```txt
app/core/config.py
```

Adicionar configuração para output:

```python
OUTPUT_DIR = BASE_DIR / "outputs"
```

O arquivo deve ficar equivalente a:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

MAX_VIDEO_SIZE_MB = 200
MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024

ALLOWED_EXTENSIONS = {"mp4", "mov", "avi", "mkv", "webm"}

ALLOWED_CONTENT_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-matroska",
    "video/webm",
}
```

---

## Passo 2 — Criar schema de frames

Criar o arquivo:

```txt
app/schemas/frame_schema.py
```

Conteúdo esperado:

```python
from pydantic import BaseModel


class FrameExtractionResponse(BaseModel):
    videoId: str
    status: str
    frameIntervalSeconds: float
    totalFramesExtracted: int
    outputDir: str
    frames: list[str]
```

---

## Passo 3 — Criar service de extração de frames

Criar o arquivo:

```txt
app/services/frame_extraction_service.py
```

Conteúdo esperado:

```python
import shutil
from pathlib import Path

import cv2
from fastapi import HTTPException

from app.core.config import OUTPUT_DIR
from app.services.video_service import get_video_info


def prepare_frames_output_dir(video_id: str) -> Path:
    output_dir = OUTPUT_DIR / video_id / "frames"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


def extract_frames(video_id: str, interval_seconds: float = 0.5) -> dict:
    if interval_seconds <= 0:
        raise HTTPException(
            status_code=400,
            detail="O intervalo de extração deve ser maior que zero."
        )

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
            detail="Não foi possível abrir o vídeo para extração de frames."
        )

    fps = capture.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        capture.release()
        raise HTTPException(
            status_code=400,
            detail="Não foi possível identificar o FPS do vídeo."
        )

    frame_interval = max(1, int(fps * interval_seconds))

    output_dir = prepare_frames_output_dir(video_id)

    saved_frames = []
    current_frame_index = 0
    saved_frame_index = 1

    while True:
        success, frame = capture.read()

        if not success:
            break

        if current_frame_index % frame_interval == 0:
            frame_filename = f"frame_{saved_frame_index:06d}.jpg"
            frame_path = output_dir / frame_filename

            cv2.imwrite(str(frame_path), frame)

            saved_frames.append(frame_filename)
            saved_frame_index += 1

        current_frame_index += 1

    capture.release()

    return {
        "videoId": video_id,
        "status": "frames_extracted",
        "frameIntervalSeconds": interval_seconds,
        "totalFramesExtracted": len(saved_frames),
        "outputDir": str(output_dir),
        "frames": saved_frames,
    }
```

---

## Passo 4 — Criar route de frames

Criar o arquivo:

```txt
app/routes/frames.py
```

Conteúdo esperado:

```python
from fastapi import APIRouter, Query

from app.schemas.frame_schema import FrameExtractionResponse
from app.services.frame_extraction_service import extract_frames

router = APIRouter()


@router.post("/{video_id}/frames/extract", response_model=FrameExtractionResponse)
def extract_video_frames(
    video_id: str,
    interval_seconds: float = Query(default=0.5, gt=0)
):
    return extract_frames(video_id, interval_seconds)
```

---

## Passo 5 — Registrar router no main.py

Abrir o arquivo:

```txt
app/main.py
```

Adicionar o import:

```python
from app.routes.frames import router as frames_router
```

Registrar o router:

```python
app.include_router(
    frames_router,
    prefix="/videos",
    tags=["Frames"]
)
```

Exemplo final:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.videos import router as videos_router
from app.routes.analysis import router as analysis_router
from app.routes.processing import router as processing_router
from app.routes.frames import router as frames_router

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
app.include_router(frames_router, prefix="/videos", tags=["Frames"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

---

# Fluxo de teste manual

## 1. Rodar API

Na pasta `backend`, executar:

```bash
python -m uvicorn app.main:app --reload
```

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

## 3. Abrir Swagger

Abrir:

```txt
http://localhost:8000/docs
```

## 4. Enviar vídeo

Usar o endpoint:

```http
POST /videos/upload
```

Copiar o campo retornado:

```txt
videoId
```

## 5. Extrair frames

Usar o endpoint:

```http
POST /videos/{video_id}/frames/extract
```

Com `interval_seconds`:

```txt
0.5
```

Resposta esperada:

```json
{
  "videoId": "uuid-do-video",
  "status": "frames_extracted",
  "frameIntervalSeconds": 0.5,
  "totalFramesExtracted": 25,
  "outputDir": "app/outputs/uuid-do-video/frames",
  "frames": [
    "frame_000001.jpg",
    "frame_000002.jpg",
    "frame_000003.jpg"
  ]
}
```

## 6. Validar arquivos gerados

Verificar se os frames foram salvos em:

```txt
app/outputs/{video_id}/frames
```

## 7. Testar vídeo inexistente

Usar um ID fake:

```http
POST /videos/id-inexistente/frames/extract
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

## 8. Testar intervalo inválido

Usar:

```http
POST /videos/{video_id}/frames/extract?interval_seconds=0
```

Deve retornar erro de validação.

---

# Testes via cURL

```bash
curl -X POST "http://localhost:8000/videos/SEU_VIDEO_ID/frames/extract?interval_seconds=0.5"
```

---

# Critérios de aceite

A implementação estará pronta quando:

- API subir sem erro
- `/health` continuar funcionando
- Swagger abrir normalmente
- endpoint `POST /videos/{video_id}/frames/extract` aparecer no Swagger
- endpoint validar se o vídeo existe
- endpoint retornar `404` para vídeo inexistente
- endpoint abrir vídeo com OpenCV
- endpoint extrair frames do vídeo
- endpoint salvar frames em `app/outputs/{video_id}/frames`
- endpoint retornar quantidade de frames extraídos
- endpoint retornar lista de frames
- endpoint respeitar `interval_seconds`
- endpoint rejeitar intervalo menor ou igual a zero
- código estiver separado em:
  - `schemas/frame_schema.py`
  - `services/frame_extraction_service.py`
  - `routes/frames.py`
- `main.py` registrar o router de frames corretamente

---

# Resultado esperado após essa etapa

Após essa implementação, o backend estará preparado para o seguinte fluxo:

```txt
Upload do vídeo
→ retorno do videoId
→ processamento de metadados
→ extração de frames
→ frames salvos localmente
```

Esse fluxo servirá como base para as próximas etapas:

```txt
Frames extraídos
→ detecção de pose com MediaPipe
→ geração de landmarks corporais
→ cálculo de ângulos
→ primeiras métricas reais do squat
```
