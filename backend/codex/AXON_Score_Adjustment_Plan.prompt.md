# AXON — Plano detalhado para ajuste do Score existente

## 1. Objetivo deste documento

Este documento descreve um plano técnico e funcional para ajustar o score existente da AXON, tornando a pontuação mais realista, explicável, escalável e baseada em critérios biomecânicos claros.

A proposta não é reescrever toda a aplicação do zero. O objetivo é evoluir o score atual para um modelo mais robusto, mantendo compatibilidade com o fluxo já existente da AXON.

Este arquivo deve ser usado como guia de implementação para o Codex.

---

## 2. Contexto da AXON

A AXON é uma aplicação de análise esportiva por vídeo.

O objetivo do produto é permitir que um usuário envie um vídeo de execução de exercício e receba uma análise objetiva sobre o padrão de movimento, com métricas, score e feedback prático.

A AXON não deve ser posicionada como ferramenta médica, diagnóstica ou substituta de um profissional de saúde. O foco é análise técnica, biomecânica e evolutiva.

### Propósito central

Transformar vídeo em métricas úteis:

```txt
Vídeo
→ Extração de pose
→ Extração de métricas biomecânicas
→ Comparação com uma fonte da verdade
→ Score explicável
→ Feedback técnico
→ Dashboard de resultado
```

### Stack considerada

Frontend:

- Next.js
- React
- TypeScript
- Tailwind
- Dashboard de resultados em `/results/[videoId]`
- Exibição de score, métricas e feedback

Backend:

- Python 3.11
- FastAPI
- OpenCV
- MediaPipe
- Pipeline de análise de vídeo
- Cálculo de landmarks, ângulos e score

Pipeline atual esperado:

```txt
uploadVideo
→ processVideo
→ extractFrames
→ detectPose
→ calculateMetrics
→ analyzeMovement
→ calculateScore
→ generateFeedback
→ return result
→ frontend dashboard
```

---

## 3. Problema atual do score

O score atual precisa ser ajustado porque tende a ser simples, pouco explicável e possivelmente baseado em regras muito genéricas.

Problemas esperados:

1. Score final pouco confiável.
2. Falta de pesos claros por métrica.
3. Pouca diferenciação entre qualidade do vídeo e qualidade real do movimento.
4. Ausência de uma fonte da verdade para comparação.
5. Baixa explicabilidade do motivo da pontuação.
6. Penalizações possivelmente arbitrárias.
7. Falta de separação entre:
   - score técnico;
   - score de mobilidade;
   - score de simetria;
   - score de estabilidade;
   - confiança da análise.
8. Risco de o app parecer que está “inventando” uma nota.

---

## 4. Objetivo da nova versão do score

Criar o **AXON Movement Score**, uma pontuação de 0 a 100 baseada em pilares biomecânicos claros.

O score precisa ser:

- Explicável;
- Determinístico;
- Ajustável por exercício;
- Extensível para novos movimentos;
- Separado por sub-scores;
- Tolerante a vídeos imperfeitos;
- Transparente para o usuário;
- Fácil de testar;
- Fácil de evoluir.

---

## 5. Princípio mais importante

O score final não deve sair diretamente do vídeo.

O modelo correto é:

```txt
Vídeo
→ Pose landmarks
→ Métricas brutas
→ Métricas normalizadas
→ Comparação com referência
→ Penalizações e bônus
→ Sub-scores
→ Score final
→ Feedback explicável
```

Não fazer:

```txt
Vídeo
→ Score final direto
```

---

## 6. Metodologias usadas como inspiração

A AXON deve criar uma metodologia própria, mas pode se inspirar em métodos consolidados de avaliação funcional e biomecânica.

### 6.1. MCS — Movement Competency Screen

Usar como referência principal para competência de movimento.

Aproveitar:

- Avaliação de padrões fundamentais;
- Critérios por movimento;
- Competência global;
- Análise de execução técnica;
- Controle de padrões motores.

### 6.2. FMS — Functional Movement Screen

Usar como referência complementar.

Aproveitar:

- Mobilidade;
- Estabilidade;
- Assimetria;
- Qualidade do padrão de movimento.

Não usar o FMS como diagnóstico nem como promessa de predição de lesão.

### 6.3. LESS — Landing Error Scoring System

Usar futuramente para saltos e aterrissagens.

Aproveitar:

- Valgo dinâmico de joelho;
- Controle de aterrissagem;
- Mecânica de membros inferiores.

### 6.4. Y-Balance / SEBT

Usar futuramente para equilíbrio dinâmico e controle unilateral.

Aproveitar:

- Assimetria;
- Estabilidade unilateral;
- Controle de tronco e quadril.

---

## 7. Nova metodologia proposta

Nome sugerido:

```txt
AXON Movement Score
```

Ou, em uma camada mais técnica:

```txt
AXON Movement Competency Framework
```

A metodologia deve gerar um score final de 0 a 100.

O score final deve ser composto por 5 pilares:

| Pilar | Peso inicial |
|---|---:|
| Mobilidade | 20% |
| Estabilidade | 20% |
| Simetria | 20% |
| Controle motor | 25% |
| Confiabilidade da análise | 15% |

Total: 100%.

---

## 8. Sub-scores obrigatórios

O backend deve retornar, no mínimo:

```json
{
  "final_score": 78,
  "classification": "Bom padrão, com pequenos ajustes",
  "sub_scores": {
    "mobility": 82,
    "stability": 74,
    "symmetry": 69,
    "motor_control": 80,
    "analysis_confidence": 91
  }
}
```

Esses sub-scores precisam ser exibidos no frontend.

---

## 9. Classificação do score final

Usar a seguinte classificação inicial:

| Faixa | Classificação | Interpretação |
|---:|---|---|
| 85–100 | Excelente | Movimento muito consistente, com poucas ou nenhuma compensação relevante |
| 70–84 | Bom | Movimento adequado, com pequenos pontos de melhoria |
| 50–69 | Atenção | Compensações relevantes detectadas |
| 30–49 | Baixo | Baixa qualidade técnica ou limitações importantes |
| 0–29 | Inconclusivo ou crítico | Movimento muito limitado ou análise pouco confiável |

Importante: evitar termos médicos como “alto risco de lesão”, “diagnóstico”, “patologia” ou “tratamento”.

---

## 10. Movimentos prioritários para o MVP

O ajuste deve focar inicialmente no exercício já existente na AXON.

Considerando o histórico do produto, o movimento inicial principal é:

```txt
Squat / Agachamento
```

Depois, preparar a arquitetura para suportar:

1. Squat;
2. Lunge;
3. Single-leg squat;
4. Hip hinge;
5. Push-up;
6. Jump landing.

A implementação inicial deve priorizar o score do Squat.

---

# PARTE 2 — REGRAS DO SCORE PARA SQUAT

## 11. Métricas necessárias para o Squat

Para o movimento de agachamento, extrair e/ou reaproveitar as seguintes métricas:

### 11.1. Métricas de mobilidade

- Profundidade do agachamento;
- Ângulo mínimo de joelho;
- Ângulo mínimo de quadril;
- Amplitude total do movimento;
- Mobilidade de tornozelo estimada;
- Capacidade de manter tronco em posição aceitável.

### 11.2. Métricas de estabilidade

- Oscilação lateral do tronco;
- Variação da pelve;
- Variação do centro estimado do corpo;
- Estabilidade durante descida;
- Estabilidade durante subida;
- Perda de controle no ponto mais baixo.

### 11.3. Métricas de simetria

- Diferença entre joelho esquerdo e direito;
- Diferença entre quadril esquerdo e direito;
- Assimetria de deslocamento lateral;
- Diferença de carga visual estimada entre os lados;
- Diferença na trajetória dos joelhos.

### 11.4. Métricas de controle motor

- Velocidade da descida;
- Velocidade da subida;
- Consistência entre repetições;
- Controle no fundo do movimento;
- Presença de compensações;
- Variação brusca entre frames.

### 11.5. Métricas de confiabilidade da análise

- Percentual de frames com pose detectada;
- Confiança média dos landmarks;
- Quantidade de landmarks essenciais ausentes;
- Qualidade da câmera;
- Enquadramento do corpo;
- Visibilidade dos pés, joelhos, quadril e tronco;
- Duração útil do vídeo;
- Número mínimo de repetições detectadas.

---

## 12. Separar qualidade do vídeo de qualidade do movimento

Uma regra crítica:

> Um vídeo ruim não deve necessariamente significar que o movimento é ruim.

Portanto, o score final precisa considerar a confiabilidade da análise separadamente.

Exemplo:

```json
{
  "final_score": 64,
  "movement_quality_score": 78,
  "analysis_confidence": 52,
  "warning": "A análise pode estar menos precisa porque alguns landmarks ficaram fora do enquadramento."
}
```

Se a confiabilidade for muito baixa, o app deve informar que a análise é inconclusiva.

---

## 13. Regras de confiabilidade

Criar thresholds iniciais:

| Condição | Regra |
|---|---|
| `analysis_confidence >= 80` | Análise confiável |
| `analysis_confidence >= 60 && < 80` | Análise aceitável com alerta |
| `analysis_confidence >= 40 && < 60` | Análise limitada |
| `analysis_confidence < 40` | Análise inconclusiva |

Se `analysis_confidence < 40`, retornar:

```json
{
  "final_score": null,
  "classification": "Análise inconclusiva",
  "reason": "A qualidade do vídeo ou a detecção corporal não foram suficientes para gerar um score confiável."
}
```

---

## 14. Fórmula inicial do score final

Criar a seguinte função:

```txt
final_score =
  mobility_score * 0.20 +
  stability_score * 0.20 +
  symmetry_score * 0.20 +
  motor_control_score * 0.25 +
  analysis_confidence_score * 0.15
```

Depois, arredondar para inteiro:

```txt
final_score = round(final_score)
```

Garantir que o score esteja sempre entre 0 e 100.

---

## 15. Score de mobilidade para Squat

### 15.1. Objetivo

Medir se o usuário consegue executar amplitude adequada no agachamento.

### 15.2. Métricas usadas

- Profundidade;
- Ângulo de joelho;
- Ângulo de quadril;
- Inclinação de tronco;
- Amplitude total.

### 15.3. Regras iniciais sugeridas

Criar uma função:

```python
calculate_mobility_score(metrics: SquatMetrics) -> ScoreComponent
```

Critérios:

| Critério | Peso dentro de mobilidade |
|---|---:|
| Profundidade | 40% |
| Ângulo de joelho | 25% |
| Ângulo de quadril | 20% |
| Inclinação de tronco | 15% |

Exemplo de saída:

```json
{
  "name": "mobility",
  "score": 82,
  "details": [
    {
      "metric": "squat_depth",
      "value": 0.86,
      "status": "good",
      "message": "Boa profundidade de agachamento."
    }
  ]
}
```

### 15.4. Penalizações

Penalizar:

- Pouca profundidade;
- Grande limitação de amplitude;
- Tronco excessivamente inclinado;
- Inconsistência grande entre repetições.

---

## 16. Score de estabilidade para Squat

### 16.1. Objetivo

Medir se o usuário mantém controle corporal durante a execução.

### 16.2. Métricas usadas

- Oscilação lateral;
- Variação do tronco;
- Controle no ponto mais baixo;
- Estabilidade na subida;
- Desvio da pelve.

### 16.3. Regras iniciais sugeridas

Criar função:

```python
calculate_stability_score(metrics: SquatMetrics) -> ScoreComponent
```

Critérios:

| Critério | Peso dentro de estabilidade |
|---|---:|
| Oscilação lateral do tronco | 30% |
| Controle da pelve | 25% |
| Estabilidade no fundo | 25% |
| Estabilidade na subida | 20% |

Penalizar:

- Oscilação lateral excessiva;
- Queda de quadril;
- Perda de controle no fundo;
- Mudanças bruscas de trajetória.

---

## 17. Score de simetria para Squat

### 17.1. Objetivo

Medir diferenças relevantes entre lado esquerdo e direito.

### 17.2. Métricas usadas

- Diferença angular entre joelhos;
- Diferença angular entre quadris;
- Deslocamento lateral do corpo;
- Diferença de trajetória dos joelhos;
- Valgo assimétrico.

### 17.3. Regras iniciais sugeridas

Criar função:

```python
calculate_symmetry_score(metrics: SquatMetrics) -> ScoreComponent
```

Critérios:

| Critério | Peso dentro de simetria |
|---|---:|
| Simetria dos joelhos | 35% |
| Simetria dos quadris | 25% |
| Deslocamento lateral | 25% |
| Trajetória dos joelhos | 15% |

Penalizar:

- Diferença grande entre joelhos;
- Um joelho colapsando mais que o outro;
- Deslocamento lateral visível;
- Compensação unilateral.

---

## 18. Score de controle motor para Squat

### 18.1. Objetivo

Medir a qualidade da coordenação durante o movimento.

### 18.2. Métricas usadas

- Tempo de descida;
- Tempo de subida;
- Suavidade da trajetória;
- Consistência entre repetições;
- Presença de compensações;
- Controle no ponto mais baixo.

### 18.3. Regras iniciais sugeridas

Criar função:

```python
calculate_motor_control_score(metrics: SquatMetrics) -> ScoreComponent
```

Critérios:

| Critério | Peso dentro de controle motor |
|---|---:|
| Consistência entre repetições | 30% |
| Suavidade do movimento | 25% |
| Controle no fundo | 20% |
| Ritmo descida/subida | 15% |
| Ausência de compensações bruscas | 10% |

Penalizar:

- Repetições muito diferentes;
- Movimento “travado” ou irregular;
- Perda de controle no fundo;
- Subida desorganizada;
- Variação brusca de velocidade.

---

## 19. Score de confiabilidade da análise

### 19.1. Objetivo

Medir se a análise pode ser considerada confiável.

### 19.2. Métricas usadas

- Percentual de frames válidos;
- Confiança média da pose;
- Visibilidade dos landmarks críticos;
- Enquadramento;
- Duração;
- Número de repetições válidas.

### 19.3. Landmarks críticos para Squat

Considerar como críticos:

- Ombros;
- Quadris;
- Joelhos;
- Tornozelos;
- Pés.

Se muitos desses landmarks estiverem ausentes, reduzir a confiança.

### 19.4. Regras iniciais sugeridas

Criar função:

```python
calculate_analysis_confidence_score(metrics: SquatMetrics) -> ScoreComponent
```

Critérios:

| Critério | Peso dentro da confiabilidade |
|---|---:|
| Frames com pose detectada | 35% |
| Confiança média dos landmarks | 30% |
| Landmarks críticos visíveis | 20% |
| Número de repetições válidas | 15% |

---

# PARTE 3 — ARQUITETURA TÉCNICA

## 20. Estrutura de pastas sugerida no backend

Criar ou ajustar a estrutura de scoring:

```txt
backend/
  app/
    modules/
      analyses/
        routes.py
        service.py
        schemas.py
      biomechanics/
        angles.py
        metrics.py
        normalization.py
      scoring/
        __init__.py
        engine.py
        schemas.py
        components.py
        classification.py
        config.py
        exercises/
          __init__.py
          squat.py
      feedback/
        generator.py
```

Caso o projeto atual tenha outra estrutura, adaptar sem quebrar o padrão existente.

---

## 21. Criar camada de scoring isolada

O cálculo do score deve ficar isolado em um módulo próprio.

Não deixar a lógica de score espalhada em:

- rota;
- controller;
- processamento de vídeo;
- frontend;
- função de upload.

Criar uma camada central:

```python
app/modules/scoring/engine.py
```

Responsabilidade:

- Receber métricas biomecânicas;
- Identificar o exercício;
- Chamar o scoring específico;
- Gerar score final;
- Gerar classificação;
- Retornar detalhes explicáveis.

---

## 22. Contrato de entrada do scoring

Criar um schema de entrada.

Exemplo:

```python
class ScoringInput(BaseModel):
    analysis_id: str
    exercise_type: str
    metrics: dict
    reps: list[dict] | None = None
    pose_quality: dict | None = None
```

---

## 23. Contrato de saída do scoring

Criar um schema de saída.

Exemplo:

```python
class ScoreComponent(BaseModel):
    name: str
    score: int
    weight: float
    status: str
    details: list[dict]

class ScoreResult(BaseModel):
    final_score: int | None
    movement_quality_score: int | None
    analysis_confidence: int
    classification: str
    summary: str
    components: list[ScoreComponent]
    warnings: list[str]
    recommendations: list[str]
```

---

## 24. Estrutura esperada de resposta da API

A API deve retornar algo próximo de:

```json
{
  "analysis_id": "uuid",
  "exercise_type": "squat",
  "score": {
    "final_score": 78,
    "movement_quality_score": 76,
    "analysis_confidence": 91,
    "classification": "Bom padrão, com pequenos ajustes",
    "summary": "Seu agachamento apresenta boa mobilidade geral, mas há leve assimetria entre os joelhos.",
    "components": [
      {
        "name": "mobility",
        "score": 82,
        "weight": 0.2,
        "status": "good",
        "details": []
      },
      {
        "name": "stability",
        "score": 74,
        "weight": 0.2,
        "status": "attention",
        "details": []
      },
      {
        "name": "symmetry",
        "score": 69,
        "weight": 0.2,
        "status": "attention",
        "details": []
      },
      {
        "name": "motor_control",
        "score": 80,
        "weight": 0.25,
        "status": "good",
        "details": []
      },
      {
        "name": "analysis_confidence",
        "score": 91,
        "weight": 0.15,
        "status": "reliable",
        "details": []
      }
    ],
    "warnings": [],
    "recommendations": [
      "Observe o alinhamento dos joelhos durante a descida.",
      "Tente manter o tronco mais estável no ponto mais baixo."
    ]
  }
}
```

---

## 25. Configuração por exercício

Criar uma configuração centralizada para pesos.

Exemplo:

```python
SCORE_WEIGHTS = {
    "squat": {
        "mobility": 0.20,
        "stability": 0.20,
        "symmetry": 0.20,
        "motor_control": 0.25,
        "analysis_confidence": 0.15
    }
}
```

Essa configuração deve ficar em:

```txt
app/modules/scoring/config.py
```

Evitar hardcode espalhado.

---

## 26. Suporte futuro a múltiplos exercícios

O engine deve suportar roteamento por exercício:

```python
def calculate_score(input: ScoringInput) -> ScoreResult:
    if input.exercise_type == "squat":
        return calculate_squat_score(input)
    raise UnsupportedExerciseError(...)
```

Ou usar um registry:

```python
SCORING_REGISTRY = {
    "squat": calculate_squat_score,
    "lunge": calculate_lunge_score,
}
```

Recomendação: usar registry.

---

# PARTE 4 — FONTE DA VERDADE

## 27. Criar uma fonte da verdade para critérios

A AXON precisa de uma camada central que defina os critérios esperados por exercício.

Essa fonte da verdade pode começar como arquivo Python, JSON ou YAML.

Recomendação inicial:

```txt
backend/app/modules/scoring/exercises/squat.py
```

Ou:

```txt
backend/app/modules/scoring/rules/squat_rules.json
```

Para o MVP, Python é suficiente. Depois pode migrar para banco.

---

## 28. Exemplo de fonte da verdade para Squat

Criar algo semelhante:

```python
SQUAT_REFERENCE = {
    "depth": {
        "excellent": {"min": 0.85},
        "good": {"min": 0.70},
        "attention": {"min": 0.50},
        "poor": {"min": 0.0}
    },
    "knee_symmetry_diff": {
        "excellent": {"max": 5},
        "good": {"max": 10},
        "attention": {"max": 18},
        "poor": {"max": 999}
    },
    "trunk_inclination": {
        "excellent": {"max": 15},
        "good": {"max": 25},
        "attention": {"max": 35},
        "poor": {"max": 999}
    }
}
```

Observação: os valores acima são placeholders iniciais. Devem ser ajustáveis.

---

## 29. Não travar o produto esperando valores perfeitos

Como ainda não existe validação científica própria da AXON, iniciar com thresholds configuráveis.

Criar comentários claros no código:

```python
# Initial heuristic thresholds.
# These values must be calibrated with real user videos and expert review.
```

---

## 30. Versão inicial do método

Adicionar versionamento ao score.

Exemplo:

```json
{
  "score_method": "AXON_MOVEMENT_SCORE",
  "score_version": "1.0.0"
}
```

Isso é importante para evolução futura.

Quando os critérios mudarem, a versão deve mudar.

---

# PARTE 5 — BACKEND: IMPLEMENTAÇÃO DETALHADA

## 31. Tarefa 1 — Mapear score atual

Antes de alterar, localizar:

- Onde o score atual é calculado;
- Quais métricas entram no cálculo;
- Qual formato retorna para o frontend;
- Quais campos o frontend espera;
- Se há testes existentes.

Criar comentário ou documentação curta no PR:

```txt
Score atual localizado em: [arquivo/função]
Problemas encontrados:
- regra X hardcoded
- sem subscore
- sem confidence score
- sem explicabilidade
```

---

## 32. Tarefa 2 — Criar schemas do scoring

Criar arquivo:

```txt
backend/app/modules/scoring/schemas.py
```

Com modelos:

```python
from pydantic import BaseModel
from typing import Any, Literal

class ScoreDetail(BaseModel):
    metric: str
    value: Any | None = None
    status: str
    message: str

class ScoreComponent(BaseModel):
    name: str
    score: int
    weight: float
    status: str
    details: list[ScoreDetail] = []

class ScoreResult(BaseModel):
    final_score: int | None
    movement_quality_score: int | None
    analysis_confidence: int
    classification: str
    summary: str
    components: list[ScoreComponent]
    warnings: list[str] = []
    recommendations: list[str] = []
    score_method: str = "AXON_MOVEMENT_SCORE"
    score_version: str = "1.0.0"
```

Ajustar o código para seguir o padrão do projeto.

---

## 33. Tarefa 3 — Criar helpers de normalização

Criar arquivo:

```txt
backend/app/modules/scoring/components.py
```

Funções úteis:

```python
def clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))

def weighted_score(items: list[tuple[float, float]]) -> int:
    # items = [(score, weight), ...]
    total_weight = sum(weight for _, weight in items)
    if total_weight == 0:
        return 0
    score = sum(score * weight for score, weight in items) / total_weight
    return clamp_score(score)

def get_status_from_score(score: int) -> str:
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 50:
        return "attention"
    if score >= 30:
        return "poor"
    return "critical"
```

---

## 34. Tarefa 4 — Criar classification.py

Criar arquivo:

```txt
backend/app/modules/scoring/classification.py
```

Função:

```python
def classify_score(score: int | None, analysis_confidence: int) -> str:
    if score is None or analysis_confidence < 40:
        return "Análise inconclusiva"

    if score >= 85:
        return "Excelente padrão de movimento"
    if score >= 70:
        return "Bom padrão, com pequenos ajustes"
    if score >= 50:
        return "Compensações relevantes detectadas"
    if score >= 30:
        return "Baixa competência de movimento"
    return "Análise crítica ou muito limitada"
```

---

## 35. Tarefa 5 — Criar scoring/config.py

Criar arquivo:

```txt
backend/app/modules/scoring/config.py
```

Adicionar:

```python
SCORE_METHOD = "AXON_MOVEMENT_SCORE"
SCORE_VERSION = "1.0.0"

SCORE_WEIGHTS = {
    "squat": {
        "mobility": 0.20,
        "stability": 0.20,
        "symmetry": 0.20,
        "motor_control": 0.25,
        "analysis_confidence": 0.15,
    }
}

MIN_CONFIDENCE_TO_SCORE = 40
LOW_CONFIDENCE_WARNING = 60
```

---

## 36. Tarefa 6 — Criar scoring/exercises/squat.py

Criar arquivo:

```txt
backend/app/modules/scoring/exercises/squat.py
```

Implementar funções:

```python
def calculate_squat_score(scoring_input: ScoringInput) -> ScoreResult:
    mobility = calculate_squat_mobility_score(scoring_input.metrics)
    stability = calculate_squat_stability_score(scoring_input.metrics)
    symmetry = calculate_squat_symmetry_score(scoring_input.metrics)
    motor_control = calculate_squat_motor_control_score(scoring_input.metrics)
    confidence = calculate_squat_analysis_confidence_score(scoring_input.metrics)

    if confidence.score < MIN_CONFIDENCE_TO_SCORE:
        return build_inconclusive_result(...)

    movement_quality_score = weighted_score([
        (mobility.score, 0.20),
        (stability.score, 0.20),
        (symmetry.score, 0.20),
        (motor_control.score, 0.25),
    ])

    final_score = weighted_score([
        (mobility.score, 0.20),
        (stability.score, 0.20),
        (symmetry.score, 0.20),
        (motor_control.score, 0.25),
        (confidence.score, 0.15),
    ])

    return ScoreResult(...)
```

---

## 37. Tarefa 7 — Criar scoring/engine.py

Criar arquivo:

```txt
backend/app/modules/scoring/engine.py
```

Implementar registry:

```python
from app.modules.scoring.exercises.squat import calculate_squat_score

SCORING_REGISTRY = {
    "squat": calculate_squat_score,
}

def calculate_score(scoring_input: ScoringInput) -> ScoreResult:
    exercise_type = scoring_input.exercise_type.lower()

    scoring_function = SCORING_REGISTRY.get(exercise_type)

    if not scoring_function:
        raise ValueError(f"Unsupported exercise type: {exercise_type}")

    return scoring_function(scoring_input)
```

---

## 38. Tarefa 8 — Adaptar pipeline existente

No ponto atual onde o score é calculado, trocar a lógica antiga para usar:

```python
score_result = calculate_score(
    ScoringInput(
        analysis_id=analysis_id,
        exercise_type=exercise_type,
        metrics=metrics,
        reps=reps,
        pose_quality=pose_quality,
    )
)
```

Importante:

- Não quebrar a resposta atual do frontend.
- Se necessário, manter campos antigos temporariamente.
- Adicionar novos campos em `score`.

---

## 39. Tarefa 9 — Gerar feedback a partir dos componentes

O feedback não deve ser genérico.

Ele deve usar os componentes:

Exemplo:

```python
if symmetry.score < 70:
    recommendations.append("Foi detectada assimetria entre os lados. Observe o alinhamento dos joelhos durante a descida.")

if mobility.score < 70:
    recommendations.append("A amplitude do movimento pode ser melhorada. Tente aumentar a profundidade de forma controlada.")

if stability.score < 70:
    recommendations.append("Houve oscilação durante o movimento. Foque em manter o tronco estável.")
```

Criar:

```txt
backend/app/modules/feedback/generator.py
```

Ou ajustar o arquivo existente.

---

# PARTE 6 — FRONTEND: IMPLEMENTAÇÃO DETALHADA

## 40. Objetivo no frontend

O frontend deve deixar claro que o score é composto por sub-scores.

O usuário precisa entender:

- Nota final;
- Classificação;
- Pontos fortes;
- Pontos de atenção;
- Confiança da análise;
- Por que recebeu aquela nota.

---

## 41. Ajustar tipagens

Criar ou ajustar tipos TypeScript:

```ts
export type ScoreComponent = {
  name: string;
  score: number;
  weight: number;
  status: string;
  details: {
    metric: string;
    value?: unknown;
    status: string;
    message: string;
  }[];
};

export type ScoreResult = {
  final_score: number | null;
  movement_quality_score: number | null;
  analysis_confidence: number;
  classification: string;
  summary: string;
  components: ScoreComponent[];
  warnings: string[];
  recommendations: string[];
  score_method: string;
  score_version: string;
};
```

---

## 42. Ajustar tela de resultado

Na página:

```txt
/results/[videoId]
```

Exibir:

1. Score final;
2. Classificação;
3. Resumo;
4. Confidence badge;
5. Sub-scores;
6. Recomendações;
7. Alertas de baixa confiabilidade.

---

## 43. Visual recomendado para score final

Exemplo de UX:

```txt
AXON Movement Score
78 / 100
Bom padrão, com pequenos ajustes
```

Abaixo:

```txt
Confiança da análise: 91%
```

Se a confiança for baixa:

```txt
Atenção: a análise pode estar menos precisa porque o corpo não ficou totalmente enquadrado.
```

---

## 44. Visual recomendado para sub-scores

Exibir cards:

```txt
Mobilidade: 82
Estabilidade: 74
Simetria: 69
Controle motor: 80
Confiabilidade: 91
```

Cada card deve ter:

- nome;
- score;
- status;
- descrição curta;
- cor ou indicador visual.

---

## 45. Não esconder análise inconclusiva

Se `final_score` for `null`, o frontend não deve mostrar `0`.

Mostrar:

```txt
Análise inconclusiva
Não foi possível gerar um score confiável com este vídeo.
```

E sugestões:

- Grave com o corpo inteiro visível;
- Evite cortes nos pés e joelhos;
- Use boa iluminação;
- Posicione a câmera lateral ou frontal conforme orientação;
- Grave pelo menos 2 repetições completas.

---

## 46. Evitar linguagem médica

Não usar:

- risco de lesão;
- diagnóstico;
- patologia;
- tratamento;
- reabilitação.

Usar:

- ponto de atenção;
- compensação;
- padrão de movimento;
- qualidade técnica;
- controle;
- estabilidade;
- mobilidade.

---

# PARTE 7 — TESTES

## 47. Testes unitários obrigatórios

Criar testes para:

```txt
calculate_mobility_score
calculate_stability_score
calculate_symmetry_score
calculate_motor_control_score
calculate_analysis_confidence_score
calculate_squat_score
classify_score
clamp_score
weighted_score
```

---

## 48. Cenários mínimos de teste

### Cenário 1 — Movimento excelente

Input:

- Boa profundidade;
- Boa simetria;
- Boa estabilidade;
- Boa confiança de pose.

Esperado:

- `final_score >= 85`;
- classificação excelente;
- sem warnings críticos.

---

### Cenário 2 — Movimento bom com pequena assimetria

Input:

- Boa profundidade;
- Pequena assimetria de joelho;
- Boa confiança.

Esperado:

- score entre 70 e 84;
- recomendação sobre alinhamento;
- componente de simetria abaixo dos demais.

---

### Cenário 3 — Baixa mobilidade

Input:

- Pouca profundidade;
- Ângulos limitados;
- Boa qualidade de vídeo.

Esperado:

- mobility abaixo de 70;
- recomendação sobre amplitude;
- final_score penalizado.

---

### Cenário 4 — Baixa confiabilidade do vídeo

Input:

- Poucos frames válidos;
- Landmarks críticos ausentes;
- Confiança baixa.

Esperado:

- `final_score = null`;
- classification = "Análise inconclusiva";
- warning explicando motivo.

---

### Cenário 5 — Score nunca ultrapassa limites

Input:

- Valores extremos.

Esperado:

- Nenhum componente abaixo de 0;
- Nenhum componente acima de 100.

---

## 49. Testes de contrato da API

Garantir que a resposta inclua:

- `final_score`;
- `movement_quality_score`;
- `analysis_confidence`;
- `classification`;
- `components`;
- `warnings`;
- `recommendations`;
- `score_method`;
- `score_version`.

---

# PARTE 8 — CRITÉRIOS DE ACEITE

## 50. Critérios funcionais

A implementação será considerada concluída quando:

1. O score final for calculado com base em sub-scores.
2. O score de confiabilidade for separado da qualidade do movimento.
3. O usuário conseguir entender por que recebeu determinada nota.
4. O frontend exibir os sub-scores.
5. Vídeos ruins não retornarem score falso.
6. O backend suportar versionamento do método de score.
7. O cálculo do score estiver isolado em módulo próprio.
8. Existirem testes unitários para as principais funções.
9. O score atual da AXON for substituído sem quebrar o fluxo principal.
10. O método estiver preparado para novos exercícios.

---

## 51. Critérios técnicos

1. Não deixar regra de score hardcoded em controller/route.
2. Não calcular score no frontend.
3. Não retornar score `0` para análise inconclusiva.
4. Não misturar feedback com cálculo matemático.
5. Não usar termos médicos.
6. Não quebrar compatibilidade com o dashboard atual.
7. Usar tipagem clara no backend e frontend.
8. Manter funções pequenas e testáveis.
9. Documentar thresholds iniciais como heurísticos.
10. Centralizar pesos e critérios.

---

# PARTE 9 — ROADMAP DE IMPLEMENTAÇÃO

## 52. Fase 1 — Refatoração segura do score atual

Objetivo:

- Isolar score em um módulo próprio;
- Manter comportamento atual funcionando;
- Criar schemas;
- Criar engine.

Entregáveis:

- `scoring/engine.py`;
- `scoring/schemas.py`;
- `scoring/config.py`;
- testes básicos.

---

## 53. Fase 2 — Novo score para Squat

Objetivo:

- Implementar o AXON Movement Score para agachamento.

Entregáveis:

- `scoring/exercises/squat.py`;
- cálculo de sub-scores;
- classificação;
- recomendações;
- confidence score.

---

## 54. Fase 3 — Ajuste do frontend

Objetivo:

- Exibir score final e sub-scores.

Entregáveis:

- tipos TypeScript;
- cards de sub-score;
- alertas de confiabilidade;
- tratamento de análise inconclusiva.

---

## 55. Fase 4 — Validação com vídeos reais

Objetivo:

- Ajustar thresholds com base em vídeos reais.

Entregáveis:

- lista de vídeos de teste;
- tabela de resultados;
- comparação entre score esperado e score calculado;
- ajustes dos thresholds.

---

## 56. Fase 5 — Preparação para novos exercícios

Objetivo:

- Tornar o motor extensível.

Entregáveis:

- registry por exercício;
- documentação para adicionar novo exercício;
- esqueleto para `lunge.py`.

---

# PARTE 10 — BACKLOG DETALHADO PARA CODEX

## 57. Backend

### Item 1 — Criar módulo de scoring

Criar:

```txt
backend/app/modules/scoring/
```

Com:

```txt
__init__.py
engine.py
schemas.py
components.py
classification.py
config.py
```

### Item 2 — Criar scoring para Squat

Criar:

```txt
backend/app/modules/scoring/exercises/squat.py
```

### Item 3 — Integrar no pipeline atual

Substituir o cálculo antigo do score pelo novo engine.

### Item 4 — Garantir compatibilidade

Se o frontend espera `score`, manter `score`.

Mas adicionar estrutura nova:

```json
{
  "score": {
    "final_score": 78,
    "components": []
  }
}
```

### Item 5 — Criar testes

Criar testes unitários para todos os componentes principais.

---

## 58. Frontend

### Item 1 — Atualizar tipos

Criar/ajustar tipos para o novo contrato.

### Item 2 — Atualizar dashboard

Exibir:

- score final;
- classificação;
- resumo;
- sub-scores;
- recomendações;
- warnings.

### Item 3 — Tratar análise inconclusiva

Se `final_score === null`, exibir estado específico.

### Item 4 — Melhorar UX do score

Não exibir somente uma nota isolada.

Exibir o racional da pontuação.

---

# PARTE 11 — EXEMPLOS DE PAYLOAD

## 59. Exemplo de análise confiável

```json
{
  "analysis_id": "123",
  "exercise_type": "squat",
  "score": {
    "final_score": 78,
    "movement_quality_score": 76,
    "analysis_confidence": 91,
    "classification": "Bom padrão, com pequenos ajustes",
    "summary": "Seu agachamento apresenta boa mobilidade geral, mas há leve assimetria entre os joelhos.",
    "components": [
      {
        "name": "mobility",
        "score": 82,
        "weight": 0.2,
        "status": "good",
        "details": [
          {
            "metric": "squat_depth",
            "value": 0.84,
            "status": "good",
            "message": "Boa profundidade de agachamento."
          }
        ]
      },
      {
        "name": "stability",
        "score": 74,
        "weight": 0.2,
        "status": "good",
        "details": []
      },
      {
        "name": "symmetry",
        "score": 69,
        "weight": 0.2,
        "status": "attention",
        "details": [
          {
            "metric": "knee_symmetry",
            "value": 14,
            "status": "attention",
            "message": "Foi detectada leve diferença entre os joelhos."
          }
        ]
      },
      {
        "name": "motor_control",
        "score": 80,
        "weight": 0.25,
        "status": "good",
        "details": []
      },
      {
        "name": "analysis_confidence",
        "score": 91,
        "weight": 0.15,
        "status": "reliable",
        "details": []
      }
    ],
    "warnings": [],
    "recommendations": [
      "Observe o alinhamento dos joelhos durante a descida.",
      "Mantenha o tronco estável no ponto mais baixo do movimento."
    ],
    "score_method": "AXON_MOVEMENT_SCORE",
    "score_version": "1.0.0"
  }
}
```

---

## 60. Exemplo de análise inconclusiva

```json
{
  "analysis_id": "123",
  "exercise_type": "squat",
  "score": {
    "final_score": null,
    "movement_quality_score": null,
    "analysis_confidence": 32,
    "classification": "Análise inconclusiva",
    "summary": "Não foi possível gerar um score confiável com este vídeo.",
    "components": [
      {
        "name": "analysis_confidence",
        "score": 32,
        "weight": 0.15,
        "status": "critical",
        "details": [
          {
            "metric": "valid_pose_frames",
            "value": 0.31,
            "status": "critical",
            "message": "Poucos frames tiveram pose detectada com confiança suficiente."
          }
        ]
      }
    ],
    "warnings": [
      "O corpo não ficou totalmente visível durante a execução.",
      "A iluminação ou o enquadramento prejudicaram a análise."
    ],
    "recommendations": [
      "Grave novamente com o corpo inteiro visível.",
      "Evite cortar pés, joelhos, quadril e ombros.",
      "Use boa iluminação.",
      "Posicione a câmera em um ângulo estável."
    ],
    "score_method": "AXON_MOVEMENT_SCORE",
    "score_version": "1.0.0"
  }
}
```

---

# PARTE 12 — PROMPT DIRETO PARA O CODEX

## 61. Instrução principal

Implementar uma nova camada de score para a AXON chamada `AXON Movement Score`.

O objetivo é substituir o score atual por um modelo composto por sub-scores:

- mobility;
- stability;
- symmetry;
- motor_control;
- analysis_confidence.

O score final deve ser de 0 a 100 e precisa ser explicável.

A implementação deve priorizar o exercício `squat`.

Não reescrever toda a aplicação. Refatorar o mínimo necessário, mantendo o fluxo atual funcionando.

---

## 62. Regras obrigatórias

1. O score deve ser calculado no backend.
2. A lógica deve ficar isolada em um módulo `scoring`.
3. O frontend apenas consome e exibe o resultado.
4. O score deve retornar componentes e recomendações.
5. Vídeo com baixa confiança não deve retornar score falso.
6. A resposta deve suportar `final_score = null`.
7. O método deve ter versão.
8. O score precisa ser extensível para novos exercícios.
9. Não usar termos médicos.
10. Criar testes unitários.

---

## 63. Resultado esperado

Ao final, uma análise deve retornar uma estrutura semelhante a:

```json
{
  "score": {
    "final_score": 78,
    "movement_quality_score": 76,
    "analysis_confidence": 91,
    "classification": "Bom padrão, com pequenos ajustes",
    "summary": "Seu agachamento apresenta boa mobilidade geral, mas há leve assimetria entre os joelhos.",
    "components": [],
    "warnings": [],
    "recommendations": [],
    "score_method": "AXON_MOVEMENT_SCORE",
    "score_version": "1.0.0"
  }
}
```

---

# PARTE 13 — OBSERVAÇÕES FINAIS

## 64. O que evitar

Evitar:

- Score mágico;
- Diagnóstico médico;
- Predição de lesão;
- Regras escondidas no frontend;
- Thresholds espalhados no código;
- Score 0 para vídeo inconclusivo;
- Feedback genérico;
- Reescrita completa da aplicação sem necessidade.

---

## 65. O que priorizar

Priorizar:

- Score explicável;
- Sub-scores;
- Confiança da análise;
- Fonte da verdade centralizada;
- Preparação para novos exercícios;
- Testes;
- UX clara no dashboard.

---

## 66. Próximo passo depois da implementação

Depois da primeira versão técnica, criar uma planilha ou dataset simples com vídeos reais para calibrar o score.

Tabela sugerida:

| Vídeo | Exercício | Score esperado | Score AXON | Diferença | Observações |
|---|---|---:|---:|---:|---|
| squat_001.mp4 | Squat | 80 | 76 | -4 | Leve assimetria |
| squat_002.mp4 | Squat | 60 | 64 | +4 | Pouca profundidade |
| squat_003.mp4 | Squat | Inconclusivo | null | - | Vídeo cortado |

Essa calibração é essencial para transformar o score de heurístico em um método cada vez mais confiável.

---

# Checklist final para o Codex

- [ ] Mapear onde o score atual é calculado.
- [ ] Criar módulo `scoring`.
- [ ] Criar schemas de entrada e saída.
- [ ] Criar helpers de score.
- [ ] Criar classificação.
- [ ] Criar configuração de pesos.
- [ ] Criar scoring específico para `squat`.
- [ ] Integrar engine no pipeline atual.
- [ ] Retornar sub-scores.
- [ ] Retornar confidence score.
- [ ] Tratar análise inconclusiva.
- [ ] Ajustar feedback baseado nos componentes.
- [ ] Atualizar contrato da API.
- [ ] Atualizar tipos no frontend.
- [ ] Atualizar dashboard de resultados.
- [ ] Criar testes unitários.
- [ ] Garantir que score sempre fique entre 0 e 100.
- [ ] Garantir que baixa confiança não vire score 0.
- [ ] Adicionar `score_method`.
- [ ] Adicionar `score_version`.
- [ ] Documentar thresholds como heurísticos iniciais.
