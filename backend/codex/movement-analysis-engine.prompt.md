# movement-analysis-engine.prompt.md — Implementação do Motor de Análise Temporal do Movimento

## Contexto do projeto

Estou criando uma plataforma web chamada inicialmente **Sport AI Platform**.

A plataforma será voltada para análise esportiva por vídeo com IA, começando pelo esporte **Crossfit**.

O backend já possui:

- upload de vídeos
- processamento de vídeo
- extração de frames
- detecção de pose com MediaPipe
- geração de landmarks.json
- cálculo de métricas biomecânicas reais
- geração de metrics.json

Agora quero evoluir o backend criando a etapa de:

# Movement Analysis Engine

O objetivo desta etapa é:

- entender o movimento ao longo do tempo
- detectar repetições do squat
- identificar início, fundo e fim de cada rep
- calcular métricas por repetição
- transformar o sistema em uma engine temporal biomecânica

---

# Objetivo principal

Transformar:

```txt
análise do vídeo inteiro
```

em:

```txt
análise rep por rep
```

---

# Stack atual

- Python 3.11
- FastAPI
- OpenCV
- MediaPipe
- JSON
- Matemática vetorial
- Processamento temporal

---

# Regras importantes

## Fazer agora

- Criar estrutura modular para análise temporal
- Criar schema Pydantic
- Criar service temporal
- Criar route de movement analysis
- Registrar router no main.py
- Ler landmarks.json
- Detectar reps automaticamente
- Detectar fases do squat
- Detectar lockout
- Detectar bottom position
- Calcular métricas por repetição
- Salvar movement_analysis.json
- Retornar resumo do treino

## Não fazer agora

Não implementar:

- IA generativa
- feedback textual
- score final avançado
- machine learning
- múltiplos exercícios
- banco de dados
- websocket
- cloud
- autenticação
- Docker
- filas
- Redis
- Celery

---

# Movimento foco

## Exercício

```txt
Back Squat
```

---

# Conceito principal

A engine deve analisar:

```txt
frame a frame
```

usando:

```txt
knee angle ao longo do tempo
```

---

# Exemplo do comportamento esperado

## Início

```txt
170°
```

(atleta em pé)

↓

## Descida

```txt
150°
120°
95°
```

↓

## Fundo

```txt
70°
```

↓

## Subida

```txt
90°
130°
165°
```

↓

## Lockout

```txt
170°
```

# REP COMPLETA

---

# Estrutura nova

Adicionar:

```txt
backend/
├── app/
│   ├── routes/
│   │   └── movement.py
│   ├── services/
│   │   └── movement_analysis_service.py
│   └── schemas/
│       └── movement_schema.py
```

---

# Endpoint a implementar

## Analisar movimento

```http
POST /videos/{video_id}/movement/analyze
```

---

# Responsabilidade do endpoint

Esse endpoint deve:

1. receber o `video_id`
2. validar se o vídeo existe
3. validar se existe `landmarks.json`
4. analisar sequência temporal dos frames
5. detectar repetições
6. detectar fases do squat
7. gerar métricas por repetição
8. salvar resultado
9. retornar resumo final

---

# Conceitos obrigatórios

## 1. Rep Detection

Detectar:

- início da rep
- fundo da rep
- final da rep

---

## 2. Phase Detection

Detectar:

```txt
eccentric
bottom
concentric
lockout
```

---

## 3. Rep Segmentation

Separar:

```txt
rep 1
rep 2
rep 3
```

---

## 4. Per-rep Metrics

Cada repetição deve possuir:

- profundidade
- ângulo mínimo
- estabilidade
- duração
- velocidade básica

---

# Estrutura esperada do movement_analysis.json

Salvar em:

```txt
app/outputs/{video_id}/movement/movement_analysis.json
```

Exemplo:

```json
{
  "videoId": "uuid",
  "movement": "squat",
  "totalReps": 3,
  "reps": [
    {
      "rep": 1,
      "startFrame": 12,
      "bottomFrame": 28,
      "endFrame": 44,
      "depth": "below_parallel",
      "minKneeAngle": 72.4,
      "stabilityScore": 88,
      "durationFrames": 32
    }
  ]
}
```

---

# Lógica de detecção da rep

## Regra principal

Usar:
```txt
ângulo do joelho
```

---

# Estados esperados

## Standing

```txt
kneeAngle > 150
```

---

## Descending

Ângulo diminuindo continuamente.

---

## Bottom

Menor ângulo detectado.

---

## Ascending

Ângulo aumentando.

---

## Lockout

```txt
kneeAngle > 160
```

---

# Regras da detecção

## Início da rep

Quando:

```txt
kneeAngle sai do lockout
```

---

## Fundo da rep

Quando:

```txt
menor kneeAngle encontrado
```

---

## Final da rep

Quando:

```txt
kneeAngle volta para lockout
```

---

# Regras importantes

## Evitar falsas reps

Ignorar movimentos pequenos.

Só considerar rep válida quando:

```txt
minKneeAngle < 120
```

---

# Métricas por repetição

## 1. minKneeAngle

Menor ângulo da rep.

---

## 2. depth

Classificar:

```txt
above_parallel
parallel
below_parallel
```

---

## 3. stabilityScore

Score simples:
```txt
0 → 100
```

---

## 4. durationFrames

Quantidade de frames da rep.

---

## 5. averageVelocity

Velocidade simples baseada em:
- duração
- variação angular

---

# Schema esperado

Criar:

```txt
app/schemas/movement_schema.py
```

Conteúdo esperado:

```python
from pydantic import BaseModel


class RepAnalysis(BaseModel):
    rep: int
    startFrame: int
    bottomFrame: int
    endFrame: int
    depth: str
    minKneeAngle: float
    stabilityScore: int
    durationFrames: int
    averageVelocity: float


class MovementAnalysisResponse(BaseModel):
    videoId: str
    movement: str
    totalReps: int
    reps: list[RepAnalysis]
```

---

# Service esperado

Criar:

```txt
app/services/movement_analysis_service.py
```

---

# Regras do service

O service deve:

- abrir landmarks.json
- iterar frame a frame
- calcular knee angle continuamente
- detectar transições de estado
- detectar reps
- montar estrutura final
- salvar movement_analysis.json

---

# Landmarks obrigatórios

Usar:

```txt
left_hip
left_knee
left_ankle
right_hip
right_knee
right_ankle
```

---

# Regras da implementação

## Pode usar média entre pernas

Exemplo:

```txt
average(left_knee_angle, right_knee_angle)
```

---

# Estrutura da máquina de estados

A implementação deve possuir estados como:

```txt
standing
descending
bottom
ascending
lockout
```

---

# Sugestão técnica

Criar:

```python
current_state
current_rep
rep_started
```

---

# Route esperada

Criar:

```txt
app/routes/movement.py
```

Conteúdo esperado:

```python
from fastapi import APIRouter

from app.schemas.movement_schema import MovementAnalysisResponse
from app.services.movement_analysis_service import analyze_movement

router = APIRouter()


@router.post(
    "/{video_id}/movement/analyze",
    response_model=MovementAnalysisResponse,
)
def analyze_video_movement(video_id: str):
    return analyze_movement(video_id)
```

---

# Atualizar main.py

Adicionar import:

```python
from app.routes.movement import router as movement_router
```

Registrar router:

```python
app.include_router(
    movement_router,
    prefix="/videos",
    tags=["Movement"]
)
```

---

# Fluxo esperado

```txt
Upload
→ frames
→ pose detection
→ biomechanics
→ movement analysis
```

---

# Fluxo de teste

## 1. Upload

```http
POST /videos/upload
```

---

## 2. Frames

```http
POST /videos/{video_id}/frames/extract
```

---

## 3. Pose

```http
POST /videos/{video_id}/pose/detect
```

---

## 4. Metrics

```http
POST /videos/{video_id}/metrics/calculate
```

---

## 5. Movement Analysis

```http
POST /videos/{video_id}/movement/analyze
```

---

# Resposta esperada

```json
{
  "videoId": "uuid",
  "movement": "squat",
  "totalReps": 3,
  "reps": [
    {
      "rep": 1,
      "startFrame": 12,
      "bottomFrame": 28,
      "endFrame": 44,
      "depth": "below_parallel",
      "minKneeAngle": 72.4,
      "stabilityScore": 88,
      "durationFrames": 32,
      "averageVelocity": 1.82
    }
  ]
}
```

---

# Cenários inválidos

## Sem landmarks

Retornar:

```json
{
  "detail": "Landmarks não encontrados. Execute pose detection antes."
}
```

Status:
```txt
404
```

---

# Critérios de aceite

A implementação estará pronta quando:

- API subir sem erro
- endpoint aparecer no Swagger
- endpoint validar landmarks.json
- endpoint detectar reps automaticamente
- endpoint detectar fundo da rep
- endpoint detectar lockout
- endpoint gerar movement_analysis.json
- endpoint retornar reps segmentadas
- endpoint retornar métricas por rep
- código estiver separado em:
  - `schemas/movement_schema.py`
  - `services/movement_analysis_service.py`
  - `routes/movement.py`

---

# Resultado esperado após essa etapa

Após essa implementação, o backend estará preparado para:

```txt
Análise temporal do movimento
→ reps automáticas
→ métricas por repetição
→ análise de fadiga
→ detecção de perda técnica
→ scoring engine
```

Essa etapa transforma o sistema em uma verdadeira engine de biomecânica esportiva temporal.
