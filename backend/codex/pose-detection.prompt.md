# pose-detection.prompt.md — Implementação da Detecção de Pose com MediaPipe

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
- extração de metadados reais do vídeo
- extração de frames com OpenCV em `app/outputs/{video_id}/frames`

Agora quero evoluir o backend criando a etapa de **detecção de pose**.

IMPORTANTE:

Neste momento, ainda **NÃO implementar cálculo real das métricas do squat**.

O objetivo desta etapa é apenas:

- ler os frames extraídos
- rodar MediaPipe Pose em cada frame
- detectar landmarks corporais
- salvar os landmarks em um arquivo JSON
- retornar informações sobre a detecção

---

## Objetivo desta implementação

Implementar no backend um serviço de detecção de pose usando MediaPipe.

O fluxo esperado será:

```txt
1. Usuário envia um vídeo
2. Backend salva o vídeo e retorna videoId
3. Backend extrai frames do vídeo
4. Usuário solicita detecção de pose
5. Backend lê os frames extraídos
6. Backend roda MediaPipe Pose em cada frame
7. Backend salva os landmarks em JSON
8. Backend retorna estatísticas da detecção
```

---

## Stack atual

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- python-multipart
- OpenCV
- MediaPipe
- Armazenamento local

---

## Dependência nova

Adicionar no `requirements.txt`:

```txt
mediapipe
```

Depois instalar:

```bash
pip install -r requirements.txt
```

Ou, se preferir instalar direto:

```bash
pip install mediapipe
```

---

## Regras importantes

### Fazer agora

- Criar estrutura modular para detecção de pose
- Criar schema Pydantic para resposta da detecção
- Criar service de detecção de pose
- Criar route de detecção de pose
- Registrar router no `main.py`
- Validar se o vídeo existe antes de detectar pose
- Validar se existem frames extraídos
- Ler imagens da pasta `app/outputs/{video_id}/frames`
- Rodar MediaPipe Pose nos frames
- Salvar landmarks em `app/outputs/{video_id}/pose/landmarks.json`
- Retornar total de frames processados
- Retornar total de frames com pose detectada
- Retornar caminho do arquivo JSON gerado
- Manter código simples, legível e fácil de evoluir

### Não fazer agora

Não implementar:

- cálculo de ângulos
- análise biomecânica real
- score real de performance
- detecção real de squat
- classificação de movimento
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
│   │   ├── analysis.py
│   │   ├── processing.py
│   │   └── frames.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── video_service.py
│   │   ├── analysis_service.py
│   │   ├── video_processing_service.py
│   │   └── frame_extraction_service.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── video_schema.py
│   │   ├── analysis_schema.py
│   │   ├── processing_schema.py
│   │   └── frame_schema.py
│   ├── uploads/
│   └── outputs/
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
│   │   └── pose.py
│   ├── services/
│   │   └── pose_detection_service.py
│   └── schemas/
│       └── pose_schema.py
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
│   │   ├── processing.py
│   │   ├── frames.py
│   │   └── pose.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── video_service.py
│   │   ├── analysis_service.py
│   │   ├── video_processing_service.py
│   │   ├── frame_extraction_service.py
│   │   └── pose_detection_service.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── video_schema.py
│   │   ├── analysis_schema.py
│   │   ├── processing_schema.py
│   │   ├── frame_schema.py
│   │   └── pose_schema.py
│   ├── uploads/
│   └── outputs/
├── requirements.txt
└── README.md
```

---

# Endpoint a implementar

## Detectar pose nos frames

```http
POST /videos/{video_id}/pose/detect
```

### Responsabilidade

Esse endpoint deve:

1. receber o `video_id`
2. validar se existe vídeo salvo com esse `video_id`
3. validar se existem frames extraídos em `app/outputs/{video_id}/frames`
4. ler os frames `.jpg`
5. executar MediaPipe Pose em cada frame
6. salvar landmarks detectados em JSON
7. retornar status `pose_detected`
8. retornar total de frames processados
9. retornar total de frames com pose detectada
10. retornar caminho do arquivo JSON gerado

---

# Exemplo de resposta esperada

```json
{
  "videoId": "uuid-do-video",
  "status": "pose_detected",
  "totalFramesProcessed": 25,
  "framesWithPose": 23,
  "outputFile": "app/outputs/uuid-do-video/pose/landmarks.json"
}
```

---

# Formato esperado do arquivo landmarks.json

Salvar em:

```txt
app/outputs/{video_id}/pose/landmarks.json
```

Exemplo de estrutura:

```json
{
  "videoId": "uuid-do-video",
  "frames": [
    {
      "frame": "frame_000001.jpg",
      "poseDetected": true,
      "landmarks": [
        {
          "index": 0,
          "name": "nose",
          "x": 0.5123,
          "y": 0.2312,
          "z": -0.1021,
          "visibility": 0.99
        }
      ]
    },
    {
      "frame": "frame_000002.jpg",
      "poseDetected": false,
      "landmarks": []
    }
  ]
}
```

---

# Landmarks importantes para próxima etapa

Mesmo que MediaPipe retorne todos os landmarks, garantir que o JSON preserve pelo menos:

- ombro esquerdo
- ombro direito
- quadril esquerdo
- quadril direito
- joelho esquerdo
- joelho direito
- tornozelo esquerdo
- tornozelo direito
- pé esquerdo
- pé direito

Esses pontos serão usados futuramente para calcular:

- profundidade do squat
- ângulo do joelho
- ângulo do quadril
- alinhamento do tronco
- simetria esquerda/direita

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
mediapipe
```

O arquivo deve ficar parecido com:

```txt
fastapi
uvicorn
python-multipart
opencv-python
mediapipe
```

---

## Passo 2 — Criar schema de pose

Criar o arquivo:

```txt
app/schemas/pose_schema.py
```

Conteúdo esperado:

```python
from pydantic import BaseModel


class PoseDetectionResponse(BaseModel):
    videoId: str
    status: str
    totalFramesProcessed: int
    framesWithPose: int
    outputFile: str
```

---

## Passo 3 — Criar service de detecção de pose

Criar o arquivo:

```txt
app/services/pose_detection_service.py
```

Conteúdo esperado:

```python
import json
import shutil
from pathlib import Path

import cv2
import mediapipe as mp
from fastapi import HTTPException

from app.core.config import OUTPUT_DIR
from app.services.video_service import get_video_info


POSE_LANDMARK_NAMES = {
    0: "nose",
    1: "left_eye_inner",
    2: "left_eye",
    3: "left_eye_outer",
    4: "right_eye_inner",
    5: "right_eye",
    6: "right_eye_outer",
    7: "left_ear",
    8: "right_ear",
    9: "mouth_left",
    10: "mouth_right",
    11: "left_shoulder",
    12: "right_shoulder",
    13: "left_elbow",
    14: "right_elbow",
    15: "left_wrist",
    16: "right_wrist",
    17: "left_pinky",
    18: "right_pinky",
    19: "left_index",
    20: "right_index",
    21: "left_thumb",
    22: "right_thumb",
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle",
    29: "left_heel",
    30: "right_heel",
    31: "left_foot_index",
    32: "right_foot_index",
}


def get_frames_dir(video_id: str) -> Path:
    return OUTPUT_DIR / video_id / "frames"


def prepare_pose_output_dir(video_id: str) -> Path:
    output_dir = OUTPUT_DIR / video_id / "pose"

    if output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


def serialize_landmarks(pose_landmarks) -> list[dict]:
    serialized = []

    for index, landmark in enumerate(pose_landmarks.landmark):
        serialized.append(
            {
                "index": index,
                "name": POSE_LANDMARK_NAMES.get(index, f"landmark_{index}"),
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility,
            }
        )

    return serialized


def detect_pose(video_id: str) -> dict:
    get_video_info(video_id)

    frames_dir = get_frames_dir(video_id)

    if not frames_dir.exists():
        raise HTTPException(
            status_code=404,
            detail="Frames não encontrados. Extraia os frames antes de detectar a pose."
        )

    frame_files = sorted(frames_dir.glob("*.jpg"))

    if not frame_files:
        raise HTTPException(
            status_code=404,
            detail="Nenhum frame encontrado para detecção de pose."
        )

    pose_output_dir = prepare_pose_output_dir(video_id)
    output_file = pose_output_dir / "landmarks.json"

    mp_pose = mp.solutions.pose

    frames_result = []
    frames_with_pose = 0

    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
    ) as pose:
        for frame_file in frame_files:
            image = cv2.imread(str(frame_file))

            if image is None:
                frames_result.append(
                    {
                        "frame": frame_file.name,
                        "poseDetected": False,
                        "landmarks": [],
                    }
                )
                continue

            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = pose.process(image_rgb)

            if result.pose_landmarks:
                frames_with_pose += 1
                landmarks = serialize_landmarks(result.pose_landmarks)
                pose_detected = True
            else:
                landmarks = []
                pose_detected = False

            frames_result.append(
                {
                    "frame": frame_file.name,
                    "poseDetected": pose_detected,
                    "landmarks": landmarks,
                }
            )

    json_content = {
        "videoId": video_id,
        "frames": frames_result,
    }

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(json_content, file, ensure_ascii=False, indent=2)

    return {
        "videoId": video_id,
        "status": "pose_detected",
        "totalFramesProcessed": len(frame_files),
        "framesWithPose": frames_with_pose,
        "outputFile": str(output_file),
    }
```

---

## Passo 4 — Criar route de pose

Criar o arquivo:

```txt
app/routes/pose.py
```

Conteúdo esperado:

```python
from fastapi import APIRouter

from app.schemas.pose_schema import PoseDetectionResponse
from app.services.pose_detection_service import detect_pose

router = APIRouter()


@router.post("/{video_id}/pose/detect", response_model=PoseDetectionResponse)
def detect_video_pose(video_id: str):
    return detect_pose(video_id)
```

---

## Passo 5 — Registrar router no main.py

Abrir o arquivo:

```txt
app/main.py
```

Adicionar o import:

```python
from app.routes.pose import router as pose_router
```

Registrar o router:

```python
app.include_router(
    pose_router,
    prefix="/videos",
    tags=["Pose"]
)
```

O arquivo `app/main.py` deve ficar com comportamento equivalente a:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.videos import router as videos_router
from app.routes.analysis import router as analysis_router
from app.routes.processing import router as processing_router
from app.routes.frames import router as frames_router
from app.routes.pose import router as pose_router

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
app.include_router(pose_router, prefix="/videos", tags=["Pose"])


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

## 6. Extrair frames

Antes de detectar pose, executar:

```http
POST /videos/{video_id}/frames/extract
```

Usar `interval_seconds` como:

```txt
0.5
```

---

## 7. Detectar pose

Executar:

```http
POST /videos/{video_id}/pose/detect
```

Resposta esperada:

```json
{
  "videoId": "uuid-do-video",
  "status": "pose_detected",
  "totalFramesProcessed": 25,
  "framesWithPose": 23,
  "outputFile": "app/outputs/uuid-do-video/pose/landmarks.json"
}
```

---

## 8. Validar arquivo JSON gerado

Verificar se o arquivo foi criado em:

```txt
app/outputs/{video_id}/pose/landmarks.json
```

Validar se contém:

```json
{
  "videoId": "uuid-do-video",
  "frames": []
}
```

Cada frame deve conter:

```json
{
  "frame": "frame_000001.jpg",
  "poseDetected": true,
  "landmarks": []
}
```

---

## 9. Testar sem frames

Usar um vídeo que ainda não teve frames extraídos e chamar:

```http
POST /videos/{video_id}/pose/detect
```

Resposta esperada:

```json
{
  "detail": "Frames não encontrados. Extraia os frames antes de detectar a pose."
}
```

Status esperado:

```txt
404
```

---

## 10. Testar vídeo inexistente

Usar um ID fake:

```http
POST /videos/id-inexistente/pose/detect
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

## Detectar pose

```bash
curl -X POST "http://localhost:8000/videos/SEU_VIDEO_ID/pose/detect"
```

---

# Critérios de aceite

A implementação estará pronta quando:

- API subir sem erro
- `/health` continuar funcionando
- Swagger abrir normalmente
- endpoint `POST /videos/{video_id}/pose/detect` aparecer no Swagger
- endpoint validar se o vídeo existe
- endpoint retornar `404` para vídeo inexistente
- endpoint retornar `404` quando frames não existirem
- endpoint ler os frames de `app/outputs/{video_id}/frames`
- endpoint executar MediaPipe Pose
- endpoint salvar landmarks em `app/outputs/{video_id}/pose/landmarks.json`
- endpoint retornar total de frames processados
- endpoint retornar total de frames com pose detectada
- código estiver separado em:
  - `schemas/pose_schema.py`
  - `services/pose_detection_service.py`
  - `routes/pose.py`
- `main.py` registrar o router de pose corretamente

---

# Resultado esperado após essa etapa

Após essa implementação, o backend estará preparado para o seguinte fluxo:

```txt
Upload do vídeo
→ retorno do videoId
→ extração de frames
→ detecção de pose
→ landmarks salvos em JSON
```

Esse fluxo servirá como base para as próximas etapas:

```txt
Landmarks JSON
→ cálculo de ângulos corporais
→ identificação de profundidade do squat
→ análise de estabilidade
→ primeiras métricas reais de Crossfit/Squat
```
