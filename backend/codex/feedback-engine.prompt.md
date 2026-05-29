# feedback-engine.prompt.md — Implementação da Feedback Engine

## Contexto do projeto

Estou criando uma plataforma web chamada inicialmente **Sport AI Platform**.

A plataforma será voltada para análise esportiva por vídeo com IA, começando pelo esporte **Crossfit**.

O backend já possui:

- upload de vídeos
- processamento de vídeo com OpenCV
- extração de frames
- detecção de pose com MediaPipe
- geração de landmarks.json
- cálculo de métricas biomecânicas
- geração de metrics.json
- análise temporal do movimento
- detecção automática de reps
- geração de movement_analysis.json
- cálculo de score biomecânico
- geração de scoring.json

Agora quero evoluir o backend criando a etapa de:

# Feedback Engine

O objetivo desta etapa é:

- transformar métricas e scores em feedbacks compreensíveis
- gerar resumo técnico do movimento
- listar pontos fortes
- listar pontos de melhoria
- gerar recomendações práticas para o próximo treino

---

# Objetivo principal

Transformar:

```txt
scores e métricas técnicas
```

em:

```txt
feedback claro, útil e acionável para o usuário
```

O usuário final não quer apenas ver:

```json
{
  "overallScore": 84
}
```

Ele precisa entender:

```txt
O que foi bom?
O que precisa melhorar?
O que fazer no próximo treino?
```

---

# Regras importantes

## Fazer agora

- Criar estrutura modular para feedback
- Criar schema Pydantic
- Criar feedback service
- Criar feedback route
- Registrar router no main.py
- Ler scoring.json
- Ler movement_analysis.json
- Ler metrics.json quando existir
- Gerar summary
- Gerar strengths
- Gerar improvements
- Gerar recommendations
- Salvar feedback.json
- Retornar feedback final

## Não fazer agora

Não implementar:

- IA generativa
- LLM
- OpenAI API
- machine learning
- múltiplos exercícios
- banco de dados
- autenticação
- websocket
- cloud
- Docker
- Redis
- Celery

Esta etapa deve ser baseada em regras simples, claras e determinísticas.

---

# Estrutura nova

Adicionar:

```txt
backend/
├── app/
│   ├── routes/
│   │   └── feedback.py
│   ├── services/
│   │   └── feedback_service.py
│   └── schemas/
│       └── feedback_schema.py
```

---

# Endpoint a implementar

## Gerar feedback do movimento

```http
POST /videos/{video_id}/feedback/generate
```

---

# Responsabilidade do endpoint

Esse endpoint deve:

1. receber o `video_id`
2. validar se o vídeo existe
3. validar se existe scoring.json
4. ler scoring.json
5. ler movement_analysis.json se existir
6. ler metrics.json se existir
7. gerar feedback baseado em regras
8. salvar feedback.json
9. retornar resultado final

---

# Arquivos de entrada

## Obrigatório

```txt
app/outputs/{video_id}/score/scoring.json
```

## Opcional, mas recomendado

```txt
app/outputs/{video_id}/movement/movement_analysis.json
```

## Opcional

```txt
app/outputs/{video_id}/metrics/metrics.json
```

---

# Arquivo de saída

Salvar em:

```txt
app/outputs/{video_id}/feedback/feedback.json
```

---

# Exemplo de resposta esperada

```json
{
  "videoId": "uuid",
  "status": "feedback_generated",
  "movement": "squat",
  "summary": "Sua execução teve boa profundidade, mas apresentou perda de estabilidade nas últimas repetições.",
  "strengths": [
    "Boa profundidade na maioria das repetições.",
    "Execução consistente no início da série."
  ],
  "improvements": [
    "Melhorar estabilidade dos joelhos.",
    "Evitar perda técnica nas últimas repetições."
  ],
  "recommendations": [
    "Reduza a carga e priorize controle nas próximas séries.",
    "Trabalhe mobilidade de tornozelo e ativação de glúteos."
  ]
}
```

---

# Regras de geração de feedback

A geração deve ser feita por regras simples.

---

## Overall Score

### >= 85

Resumo positivo:

```txt
Sua execução geral foi muito boa, com bom controle técnico e consistência.
```

### 70 até 84

Resumo intermediário:

```txt
Sua execução foi boa, mas ainda existem pontos técnicos importantes para melhorar.
```

### < 70

Resumo crítico:

```txt
Sua execução apresentou limitações técnicas importantes e merece atenção antes de aumentar carga ou intensidade.
```

---

## Depth Score

### >= 85

Strength:

```txt
Boa profundidade na maioria das repetições.
```

### 70 até 84

Improvement:

```txt
A profundidade está aceitável, mas ainda pode ser mais consistente.
```

### < 70

Improvement:

```txt
A profundidade do agachamento ficou abaixo do ideal em parte das repetições.
```

Recommendation:

```txt
Trabalhe mobilidade de tornozelo e quadril antes das séries principais.
```

---

## Stability Score

### >= 85

Strength:

```txt
Boa estabilidade dos joelhos durante o movimento.
```

### 70 até 84

Improvement:

```txt
Foi detectada leve instabilidade dos joelhos em algumas repetições.
```

### < 70

Improvement:

```txt
A estabilidade dos joelhos ficou abaixo do ideal.
```

Recommendation:

```txt
Reduza a carga e priorize controle dos joelhos durante a descida e subida.
```

---

## Symmetry Score

### >= 85

Strength:

```txt
Boa simetria entre os lados esquerdo e direito.
```

### 70 até 84

Improvement:

```txt
Existe uma pequena diferença entre os lados durante o movimento.
```

### < 70

Improvement:

```txt
Foi detectada assimetria relevante entre os lados.
```

Recommendation:

```txt
Inclua exercícios unilaterais para melhorar equilíbrio entre os lados.
```

---

## Consistency Score

### >= 85

Strength:

```txt
Boa consistência entre as repetições.
```

### 70 até 84

Improvement:

```txt
A execução perdeu consistência em algumas repetições.
```

### < 70

Improvement:

```txt
Houve queda importante de qualidade ao longo da série.
```

Recommendation:

```txt
Diminua o ritmo ou reduza a carga para manter qualidade técnica até o fim da série.
```

---

# Regra adicional — Fadiga

Se existir movement_analysis.json e o score das últimas reps for pior que o das primeiras:

Adicionar improvement:

```txt
Foi detectada perda técnica nas últimas repetições, possivelmente relacionada à fadiga.
```

Adicionar recommendation:

```txt
Faça séries menores ou aumente o tempo de descanso para preservar a técnica.
```

---

# Schema esperado

Criar:

```txt
app/schemas/feedback_schema.py
```

Conteúdo esperado:

```python
from pydantic import BaseModel


class FeedbackResponse(BaseModel):
    videoId: str
    status: str
    movement: str
    summary: str
    strengths: list[str]
    improvements: list[str]
    recommendations: list[str]
```

---

# Service esperado

Criar:

```txt
app/services/feedback_service.py
```

---

# Regras do service

O service deve:

- validar se o vídeo existe
- localizar scoring.json
- carregar scoring.json
- carregar movement_analysis.json, se existir
- carregar metrics.json, se existir
- gerar feedbacks por regra
- remover mensagens duplicadas
- salvar feedback.json
- retornar resultado

---

# Sugestão técnica

Criar funções separadas:

```python
load_json_file()
get_score_feedback()
generate_summary()
generate_strengths()
generate_improvements()
generate_recommendations()
detect_fatigue_pattern()
save_feedback()
generate_feedback()
```

---

# Route esperada

Criar:

```txt
app/routes/feedback.py
```

Conteúdo esperado:

```python
from fastapi import APIRouter

from app.schemas.feedback_schema import FeedbackResponse
from app.services.feedback_service import generate_feedback

router = APIRouter()


@router.post(
    "/{video_id}/feedback/generate",
    response_model=FeedbackResponse,
)
def generate_video_feedback(video_id: str):
    return generate_feedback(video_id)
```

---

# Atualizar main.py

Adicionar import:

```python
from app.routes.feedback import router as feedback_router
```

Registrar router:

```python
app.include_router(
    feedback_router,
    prefix="/videos",
    tags=["Feedback"]
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
→ feedback engine
```

---

# Fluxo de teste

## 1. Upload

```http
POST /videos/upload
```

## 2. Frames

```http
POST /videos/{video_id}/frames/extract
```

## 3. Pose

```http
POST /videos/{video_id}/pose/detect
```

## 4. Metrics

```http
POST /videos/{video_id}/metrics/calculate
```

## 5. Movement Analysis

```http
POST /videos/{video_id}/movement/analyze
```

## 6. Scoring

```http
POST /videos/{video_id}/score/calculate
```

## 7. Feedback

```http
POST /videos/{video_id}/feedback/generate
```

---

# Resposta esperada

```json
{
  "videoId": "uuid",
  "status": "feedback_generated",
  "movement": "squat",
  "summary": "Sua execução teve boa profundidade, mas apresentou perda de estabilidade nas últimas repetições.",
  "strengths": [
    "Boa profundidade na maioria das repetições.",
    "Execução consistente no início da série."
  ],
  "improvements": [
    "Melhorar estabilidade dos joelhos.",
    "Evitar perda técnica nas últimas repetições."
  ],
  "recommendations": [
    "Reduza a carga e priorize controle nas próximas séries.",
    "Trabalhe mobilidade de tornozelo e ativação de glúteos."
  ]
}
```

---

# Cenários inválidos

## Sem scoring.json

Retornar:

```json
{
  "detail": "Scoring não encontrado. Execute score calculation antes."
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
- endpoint validar scoring.json
- endpoint gerar summary
- endpoint gerar strengths
- endpoint gerar improvements
- endpoint gerar recommendations
- endpoint gerar feedback.json
- endpoint retornar feedback final
- mensagens duplicadas forem removidas
- código estiver separado em:
  - `schemas/feedback_schema.py`
  - `services/feedback_service.py`
  - `routes/feedback.py`

---

# Resultado esperado após essa etapa

Após essa implementação, o backend terá o ciclo completo:

```txt
Upload
→ Frames
→ Pose Detection
→ Metrics
→ Movement Analysis
→ Scoring
→ Feedback
```

Essa etapa transforma o sistema em uma experiência de produto mais clara para o usuário final.
