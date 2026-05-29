# scoring-engine.prompt.md — Implementação do Motor de Scoring Biomecânico

## Contexto do projeto

Estou criando uma plataforma web chamada inicialmente **Sport AI Platform**.

A plataforma será voltada para análise esportiva por vídeo com IA, começando pelo esporte **Crossfit**.

O backend já possui:

- upload de vídeos
- processamento de vídeo
- extração de frames
- detecção de pose com MediaPipe
- geração de landmarks.json
- cálculo de métricas biomecânicas
- análise temporal do movimento
- detecção automática de reps
- métricas por repetição
- geração de movement_analysis.json

Agora quero evoluir o backend criando a etapa de:

# Scoring Engine

O objetivo desta etapa é:

- transformar métricas biomecânicas em scores simples
- gerar uma nota geral do movimento
- gerar scores específicos
- transformar biomecânica em linguagem de produto

---

# Objetivo principal

Transformar:

```txt
ângulos e métricas técnicas
```

em:

```txt
scores simples e interpretáveis
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

- Criar estrutura modular para scoring
- Criar schema Pydantic
- Criar scoring service
- Criar scoring route
- Registrar router no main.py
- Ler movement_analysis.json
- Gerar score geral
- Gerar scores específicos
- Gerar consistency score
- Gerar depth score
- Gerar symmetry score
- Gerar stability score
- Salvar scoring.json
- Retornar resultado final

## Não fazer agora

Não implementar:

- IA generativa
- feedback textual
- machine learning
- múltiplos exercícios
- dashboard frontend
- banco de dados
- autenticação
- websocket
- cloud
- Docker
- Redis
- Celery

---

# Estrutura nova

Adicionar:

```txt
backend/
├── app/
│   ├── routes/
│   │   └── scoring.py
│   ├── services/
│   │   └── scoring_service.py
│   └── schemas/
│       └── scoring_schema.py
```

---

# Endpoint a implementar

## Calcular score do movimento

```http
POST /videos/{video_id}/score/calculate
```

---

# Responsabilidade do endpoint

Esse endpoint deve:

1. receber o `video_id`
2. validar se o vídeo existe
3. validar se existe movement_analysis.json
4. ler as reps detectadas
5. calcular scores biomecânicos
6. gerar overall score
7. salvar scoring.json
8. retornar resultado final

---

# Scores obrigatórios

## 1. Overall Score

Nota geral:

```txt
0 → 100
```

Deve ser baseada na média ponderada dos outros scores.

---

## 2. Depth Score

Avaliar:

- profundidade do squat
- consistência da profundidade

---

# Regras

## below_parallel

Score alto.

## parallel

Score médio.

## above_parallel

Score baixo.

---

## 3. Stability Score

Avaliar:

- estabilidade dos joelhos
- estabilidade das reps

---

## 4. Symmetry Score

Avaliar:

- diferença entre lados
- consistência bilateral

---

## 5. Consistency Score

Avaliar:

- consistência entre reps
- variação de execução
- variação angular

---

# Estrutura esperada do scoring.json

Salvar em:

```txt
app/outputs/{video_id}/score/scoring.json
```

Exemplo:

```json
{
  "videoId": "uuid",
  "status": "score_calculated",
  "movement": "squat",
  "score": {
    "overallScore": 84,
    "depthScore": 88,
    "stabilityScore": 81,
    "symmetryScore": 86,
    "consistencyScore": 79
  }
}
```

---

# Regras do Overall Score

Exemplo de pesos:

```txt
Depth → 30%
Stability → 25%
Symmetry → 20%
Consistency → 25%
```

---

# Regras do Consistency Score

Analisar:

- diferença entre reps
- diferença do knee angle
- diferença da profundidade
- diferença da estabilidade

Quanto menor a variação:
- maior o score

---

# Regras do Stability Score

Basear-se em:

- stabilityScore médio das reps

---

# Regras do Symmetry Score

Basear-se em:

- symmetryScore médio das reps

---

# Regras do Depth Score

Basear-se em:

- depth classification das reps

Exemplo:

```txt
below_parallel → 90+
parallel → 70-89
above_parallel → abaixo de 70
```

---

# Schema esperado

Criar:

```txt
app/schemas/scoring_schema.py
```

Conteúdo esperado:

```python
from pydantic import BaseModel


class ScoreBreakdown(BaseModel):
    overallScore: int
    depthScore: int
    stabilityScore: int
    symmetryScore: int
    consistencyScore: int


class ScoringResponse(BaseModel):
    videoId: str
    status: str
    movement: str
    score: ScoreBreakdown
```

---

# Service esperado

Criar:

```txt
app/services/scoring_service.py
```

---

# Regras do service

O service deve:

- abrir movement_analysis.json
- iterar pelas reps
- calcular scores
- gerar overall score
- salvar scoring.json
- retornar resultado

---

# Regras importantes

## Sempre limitar scores

Todos os scores devem ficar entre:

```txt
0 → 100
```

---

# Sugestão técnica

Criar funções separadas:

```python
calculate_depth_score()
calculate_stability_score()
calculate_symmetry_score()
calculate_consistency_score()
calculate_overall_score()
```

---

# Route esperada

Criar:

```txt
app/routes/scoring.py
```

Conteúdo esperado:

```python
from fastapi import APIRouter

from app.schemas.scoring_schema import ScoringResponse
from app.services.scoring_service import calculate_score

router = APIRouter()


@router.post(
    "/{video_id}/score/calculate",
    response_model=ScoringResponse,
)
def calculate_video_score(video_id: str):
    return calculate_score(video_id)
```

---

# Atualizar main.py

Adicionar import:

```python
from app.routes.scoring import router as scoring_router
```

Registrar router:

```python
app.include_router(
    scoring_router,
    prefix="/videos",
    tags=["Scoring"]
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
→ scoring engine
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

## 6. Scoring

```http
POST /videos/{video_id}/score/calculate
```

---

# Resposta esperada

```json
{
  "videoId": "uuid",
  "status": "score_calculated",
  "movement": "squat",
  "score": {
    "overallScore": 84,
    "depthScore": 88,
    "stabilityScore": 81,
    "symmetryScore": 86,
    "consistencyScore": 79
  }
}
```

---

# Cenários inválidos

## Sem movement_analysis.json

Retornar:

```json
{
  "detail": "Movement analysis não encontrado. Execute movement analysis antes."
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
- endpoint validar movement_analysis.json
- endpoint calcular overall score
- endpoint calcular depth score
- endpoint calcular stability score
- endpoint calcular symmetry score
- endpoint calcular consistency score
- endpoint gerar scoring.json
- endpoint retornar scores corretamente
- scores ficarem entre 0 e 100
- código estiver separado em:
  - `schemas/scoring_schema.py`
  - `services/scoring_service.py`
  - `routes/scoring.py`

---

# Resultado esperado após essa etapa

Após essa implementação, o backend estará preparado para:

```txt
Biomecânica
→ scoring
→ interpretação simplificada
→ feedback engine
→ IA Coach
```

Essa etapa transforma o sistema em um produto realmente compreensível para o usuário final.
