# biomechanics-engine.prompt.md — Implementação do Motor de Métricas Biomecânicas

## Contexto do projeto

Estou criando uma plataforma web chamada inicialmente **Sport AI Platform**.

A plataforma será voltada para análise esportiva por vídeo com IA, começando pelo esporte **Crossfit**.

O backend já possui:

- upload de vídeos
- processamento de vídeo
- extração de frames
- detecção de pose com MediaPipe
- geração de landmarks.json

Agora quero evoluir o backend criando a etapa de:

# Motor de métricas biomecânicas

O objetivo desta etapa é:

- ler os landmarks detectados
- calcular ângulos corporais
- detectar profundidade do squat
- calcular métricas biomecânicas reais
- retornar métricas reais do movimento

---

# Endpoint

```http
POST /videos/{video_id}/metrics/calculate
```

---

# Métricas a calcular

## Knee Angle

Calcular:
- ângulo médio do joelho
- menor ângulo encontrado

Usar:
- quadril
- joelho
- tornozelo

---

## Hip Angle

Usar:
- ombro
- quadril
- joelho

---

## Squat Depth

Classificar:

```txt
above_parallel
parallel
below_parallel
```

---

## Torso Inclination

Usar:
- ombro
- quadril

---

## Symmetry Score

Comparar:
- lado esquerdo
- lado direito

---

## Stability Score

Detectar:
- instabilidade básica dos joelhos

---

# Estrutura nova

```txt
app/
├── routes/
│   └── metrics.py
├── services/
│   └── biomechanics_service.py
└── schemas/
    └── metrics_schema.py
```

---

# Schema esperado

Criar:

```txt
app/schemas/metrics_schema.py
```

Conteúdo:

```python
from pydantic import BaseModel


class SquatMetrics(BaseModel):
    averageKneeAngle: float
    minKneeAngle: float
    averageHipAngle: float
    torsoInclination: float
    depthClassification: str
    symmetryScore: int
    stabilityScore: int


class MetricsCalculationResponse(BaseModel):
    videoId: str
    status: str
    movement: str
    metrics: SquatMetrics
```

---

# Service esperado

Criar:

```txt
app/services/biomechanics_service.py
```

---

# Regras do service

O service deve:

- abrir `landmarks.json`
- iterar pelos frames
- identificar landmarks necessários
- calcular ângulos
- gerar métricas finais
- salvar `metrics.json`

---

# Função de cálculo angular

Criar:

```python
def calculate_angle(a, b, c) -> float:
```

Essa função deve:

- receber 3 pontos
- usar matemática vetorial
- retornar ângulo em graus

---

# Fórmula esperada

Usar:

```python
import math
```

ou:

```python
import numpy as np
```

Aplicar:

- produto escalar
- arccos
- conversão para graus

---

# Landmarks necessários

Usar:

```txt
left_shoulder
right_shoulder
left_hip
right_hip
left_knee
right_knee
left_ankle
right_ankle
```

---

# Regras do Squat Depth

## below_parallel
Quadril abaixo do joelho.

## parallel
Quadril alinhado ao joelho.

## above_parallel
Quadril acima do joelho.

---

# Estrutura esperada do metrics.json

Salvar em:

```txt
app/outputs/{video_id}/metrics/metrics.json
```

Exemplo:

```json
{
  "videoId": "uuid",
  "movement": "squat",
  "metrics": {
    "averageKneeAngle": 92.4,
    "minKneeAngle": 71.2,
    "averageHipAngle": 85.7,
    "torsoInclination": 18.3,
    "depthClassification": "below_parallel",
    "symmetryScore": 87,
    "stabilityScore": 81
  }
}
```

---

# Route esperada

Criar:

```txt
app/routes/metrics.py
```

Conteúdo:

```python
from fastapi import APIRouter

from app.schemas.metrics_schema import MetricsCalculationResponse
from app.services.biomechanics_service import calculate_metrics

router = APIRouter()


@router.post(
    "/{video_id}/metrics/calculate",
    response_model=MetricsCalculationResponse,
)
def calculate_video_metrics(video_id: str):
    return calculate_metrics(video_id)
```

---

# Atualizar main.py

Adicionar:

```python
from app.routes.metrics import router as metrics_router
```

Registrar:

```python
app.include_router(
    metrics_router,
    prefix="/videos",
    tags=["Metrics"]
)
```

---

# Fluxo esperado

```txt
Upload do vídeo
→ extração de frames
→ pose detection
→ landmarks.json
→ cálculo biomecânico
→ metrics.json
```

---

# Fluxo de teste

## 1. Upload

```http
POST /videos/upload
```

## 2. Extrair frames

```http
POST /videos/{video_id}/frames/extract
```

## 3. Detectar pose

```http
POST /videos/{video_id}/pose/detect
```

## 4. Calcular métricas

```http
POST /videos/{video_id}/metrics/calculate
```

---

# Resposta esperada

```json
{
  "videoId": "uuid",
  "status": "metrics_calculated",
  "movement": "squat",
  "metrics": {
    "averageKneeAngle": 92.4,
    "minKneeAngle": 71.2,
    "averageHipAngle": 85.7,
    "torsoInclination": 18.3,
    "depthClassification": "below_parallel",
    "symmetryScore": 87,
    "stabilityScore": 81
  }
}
```

---

# Critérios de aceite

A implementação estará pronta quando:

- API subir sem erro
- endpoint aparecer no Swagger
- endpoint validar existência do vídeo
- endpoint validar existência do landmarks.json
- endpoint calcular ângulos reais
- endpoint calcular profundidade do squat
- endpoint gerar metrics.json
- endpoint retornar métricas biomecânicas
- código estiver separado em:
  - `schemas/metrics_schema.py`
  - `services/biomechanics_service.py`
  - `routes/metrics.py`
