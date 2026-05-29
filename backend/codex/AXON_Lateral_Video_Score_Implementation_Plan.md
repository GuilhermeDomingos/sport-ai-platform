# AXON — Plano para análise de vídeos lateralizados e novo score lateral

## 1. Objetivo

Implementar suporte para análise de vídeos **frontais** e **laterais** na AXON.

No momento do upload, o usuário deverá selecionar o tipo do vídeo:

- **Frontal**
- **Lateral**

A partir dessa seleção, o backend deverá aplicar o conjunto correto de métricas e score.

O objetivo principal é evitar que métricas criadas para vídeos frontais sejam aplicadas em vídeos laterais, gerando score errado, feedback incorreto ou penalizações injustas.

---

## 2. Contexto da AXON

A AXON é uma aplicação de análise esportiva por vídeo.

Fluxo conceitual atual:

```txt
Upload do vídeo
→ Processamento do vídeo
→ Extração de frames
→ Detecção de pose
→ Extração de landmarks
→ Cálculo de métricas biomecânicas
→ Cálculo do score
→ Geração de feedback
→ Dashboard de resultado
```

As métricas existentes foram inicialmente pensadas para vídeos frontais. Isso é adequado para medir:

- simetria esquerda/direita;
- valgo de joelho;
- alinhamento joelho-pé;
- deslocamento lateral;
- estabilidade frontal;
- diferença entre membros.

Agora queremos adicionar suporte para vídeos lateralizados, que são melhores para medir:

- profundidade do movimento;
- ângulo de joelho;
- ângulo de quadril;
- inclinação do tronco;
- amplitude;
- controle da descida;
- controle da subida;
- estabilidade no ponto mais baixo.

---

## 3. Problema atual

Se um vídeo lateral for analisado com regras frontais, a AXON pode gerar:

1. assimetria falsa;
2. penalização indevida;
3. leitura errada de joelho esquerdo/direito;
4. feedback incorreto sobre valgo;
5. score inconsistente;
6. baixa confiança do usuário no produto.

Por isso, a análise precisa ser separada por ângulo de câmera.

---

## 4. Requisito funcional principal

Adicionar um campo obrigatório no upload:

```ts
cameraView: "front" | "side"
```

No frontend, exibir:

```txt
Qual o tipo do vídeo?

( ) Frontal
( ) Lateral
```

O usuário só poderá enviar o vídeo depois de selecionar uma opção.

---

## 5. Regras de negócio

### 5.1. Seleção obrigatória

O usuário deve selecionar o tipo do vídeo antes de iniciar a análise.

Valores aceitos:

```txt
front
side
```

### 5.2. Roteamento por tipo de câmera

```txt
cameraView = front
→ usar análise frontal

cameraView = side
→ usar análise lateral
```

### 5.3. Não misturar métricas

Não aplicar métricas frontais em vídeos laterais.

Não aplicar métricas laterais em vídeos frontais.

### 5.4. Retornar tipo de análise no resultado

A resposta da API deve conter:

```json
{
  "camera_view": "side",
  "score_type": "AXON_LATERAL_MOVEMENT_SCORE"
}
```

### 5.5. Manter compatibilidade

O score frontal atual deve continuar funcionando.

A implementação lateral deve ser adicionada sem quebrar o fluxo atual.

---

# 6. Diferença entre análise frontal e lateral

## 6.1. Análise frontal

A análise frontal deve priorizar:

| Pilar | O que mede |
|---|---|
| Simetria | Diferença esquerda/direita |
| Alinhamento frontal | Valgo e trajetória dos joelhos |
| Estabilidade frontal | Oscilação lateral e queda de quadril |
| Controle motor | Consistência e compensações |
| Confiabilidade | Visibilidade dos landmarks |

## 6.2. Análise lateral

A análise lateral deve priorizar:

| Pilar | O que mede |
|---|---|
| Amplitude/profundidade | Profundidade do agachamento |
| Cinemática articular | Ângulo de joelho e quadril |
| Postura de tronco | Inclinação e estabilidade |
| Controle motor | Ritmo, fluidez, descida/subida |
| Confiabilidade | Visibilidade do lado analisado |

---

# 7. Novo score lateral

## 7.1. Nome

```txt
AXON Lateral Movement Score
```

Identificador técnico:

```txt
AXON_LATERAL_MOVEMENT_SCORE
```

Versão inicial:

```txt
1.0.0
```

## 7.2. Objetivo

Avaliar a qualidade técnica do exercício no plano lateral/sagital.

O score lateral não deve tentar avaliar fortemente simetria esquerda/direita ou valgo frontal, pois essas métricas são mais adequadas para vídeos frontais.

---

# 8. Fórmula do score lateral

O score lateral será composto por 5 componentes:

| Componente | Peso |
|---|---:|
| `amplitude_depth` | 25% |
| `joint_kinematics` | 20% |
| `trunk_posture` | 20% |
| `motor_control` | 20% |
| `analysis_confidence` | 15% |

Fórmula:

```txt
final_score =
  amplitude_depth * 0.25 +
  joint_kinematics * 0.20 +
  trunk_posture * 0.20 +
  motor_control * 0.20 +
  analysis_confidence * 0.15
```

Arredondar para inteiro e garantir intervalo entre 0 e 100.

---

# 9. Classificação do score lateral

| Score | Classificação | Interpretação |
|---:|---|---|
| 85–100 | Excelente | Movimento lateral muito consistente |
| 70–84 | Bom | Bom padrão técnico, com pequenos ajustes |
| 50–69 | Atenção | Compensações relevantes detectadas |
| 30–49 | Baixo | Baixa qualidade técnica no plano lateral |
| 0–29 | Crítico ou inconclusivo | Movimento muito limitado ou análise pouco confiável |

Evitar linguagem médica como:

- risco de lesão;
- diagnóstico;
- patologia;
- tratamento;
- reabilitação.

Usar:

- ponto de atenção;
- compensação;
- padrão de movimento;
- controle;
- estabilidade;
- amplitude;
- qualidade técnica.

---

# 10. Exercício inicial

A primeira implementação deve focar no:

```txt
Squat / Agachamento
```

A arquitetura deve permitir novos exercícios futuramente, mas o foco inicial é:

```txt
exerciseType = squat
cameraView = side
```

---

# 11. Métricas laterais para Squat

## 11.1. Profundidade do agachamento

Objetivo:

Avaliar se o usuário atinge uma profundidade adequada.

Possíveis métricas:

- posição vertical do quadril em relação ao joelho;
- ângulo mínimo de joelho;
- ângulo mínimo de quadril;
- variação vertical do quadril;
- amplitude total do movimento.

Exemplo conceitual:

```txt
Se o quadril chega próximo ou abaixo da linha do joelho
→ boa profundidade

Se o quadril permanece muito acima do joelho
→ profundidade limitada
```

## 11.2. Ângulo de joelho

Usar os landmarks:

```txt
hip → knee → ankle
```

Cálculo:

```txt
knee_angle = angle(hip, knee, ankle)
```

## 11.3. Ângulo de quadril

Usar os landmarks:

```txt
shoulder → hip → knee
```

Cálculo:

```txt
hip_angle = angle(shoulder, hip, knee)
```

## 11.4. Inclinação do tronco

Usar:

```txt
shoulder → hip
```

Calcular a inclinação da linha ombro-quadril em relação ao eixo vertical.

## 11.5. Amplitude total

Medir:

- variação vertical do quadril;
- variação angular do joelho;
- variação angular do quadril.

## 11.6. Controle no ponto mais baixo

Avaliar:

- estabilidade no fundo;
- ausência de oscilação brusca;
- ausência de perda abrupta de postura;
- controle antes da subida.

## 11.7. Ritmo de descida e subida

Medir:

- tempo de descida;
- tempo de subida;
- proporção descida/subida;
- consistência entre repetições.

## 11.8. Suavidade da trajetória

Avaliar:

- mudanças bruscas de velocidade;
- jitter;
- quebras de movimento;
- fluidez da trajetória do quadril e joelho.

---

# 12. Landmarks críticos para análise lateral

Para o vídeo lateral, considerar como landmarks críticos:

- shoulder;
- hip;
- knee;
- ankle;
- foot/toe, se disponível.

Como o vídeo lateral pode mostrar um lado mais claramente do que o outro, o sistema deve escolher o lado mais visível automaticamente.

---

# 13. Detecção do lado visível

Adicionar conceito interno:

```ts
visibleSide?: "left" | "right" | "auto"
```

Para o MVP, o usuário não precisa selecionar o lado.

O backend deve usar:

```txt
visibleSide = auto
```

Regra sugerida:

1. Calcular confiança média dos landmarks críticos do lado esquerdo.
2. Calcular confiança média dos landmarks críticos do lado direito.
3. Escolher o lado com maior confiança.
4. Em caso de empate, escolher o lado com menos landmarks ausentes.

Função sugerida:

```python
def detect_visible_side(pose_frames: list[dict]) -> Literal["left", "right"]:
    ...
```

---

# 14. Componentes do score lateral

## 14.1. `amplitude_depth`

Peso:

```txt
25%
```

Objetivo:

Avaliar profundidade e amplitude do agachamento.

Métricas usadas:

- `squat_depth_ratio`;
- `min_knee_angle`;
- `min_hip_angle`;
- `hip_vertical_displacement`;
- `range_of_motion`.

Exemplo de saída:

```json
{
  "name": "amplitude_depth",
  "score": 82,
  "weight": 0.25,
  "status": "good",
  "details": [
    {
      "metric": "squat_depth",
      "value": 0.84,
      "status": "good",
      "message": "Boa profundidade de agachamento no plano lateral."
    }
  ]
}
```

## 14.2. `joint_kinematics`

Peso:

```txt
20%
```

Objetivo:

Avaliar o comportamento do joelho e quadril durante a execução.

Métricas usadas:

- `min_knee_angle`;
- `max_knee_angle`;
- `knee_rom`;
- `min_hip_angle`;
- `max_hip_angle`;
- `hip_rom`;
- coordenação entre joelho e quadril.

## 14.3. `trunk_posture`

Peso:

```txt
20%
```

Objetivo:

Avaliar inclinação e estabilidade do tronco.

Métricas usadas:

- `max_trunk_inclination`;
- `bottom_trunk_inclination`;
- `trunk_variation`;
- estabilidade da linha ombro-quadril.

Observação:

Alguma inclinação de tronco é normal em um agachamento. Não penalizar agressivamente sem contexto.

## 14.4. `motor_control`

Peso:

```txt
20%
```

Objetivo:

Avaliar ritmo, controle e fluidez.

Métricas usadas:

- `eccentric_duration_avg`;
- `concentric_duration_avg`;
- `movement_smoothness`;
- `bottom_control`;
- `rep_consistency`.

## 14.5. `analysis_confidence`

Peso:

```txt
15%
```

Objetivo:

Medir se o vídeo tem qualidade suficiente para score.

Métricas usadas:

- `valid_pose_frame_ratio`;
- `visible_side_landmark_confidence`;
- `critical_landmarks_visible_ratio`;
- `valid_reps_count`;
- corpo inteiro visível;
- estabilidade da câmera.

---

# 15. Regra para análise inconclusiva

Se:

```txt
analysis_confidence < 40
```

Retornar:

```json
{
  "final_score": null,
  "classification": "Análise inconclusiva",
  "summary": "Não foi possível gerar um score confiável para este vídeo lateral."
}
```

Não retornar score 0.

---

# 16. Regra para baixa confiança

Se:

```txt
analysis_confidence >= 40 && analysis_confidence < 60
```

Retornar score, mas adicionar warning:

```txt
A análise lateral foi gerada com confiança limitada. Tente gravar novamente com o corpo inteiro visível, principalmente ombro, quadril, joelho e tornozelo.
```

---

# 17. Contrato de API

## 17.1. Upload

Se o upload usa `multipart/form-data`, enviar:

```txt
file: video.mp4
exerciseType: squat
cameraView: side
```

Exemplo:

```http
POST /analysis/upload
Content-Type: multipart/form-data

file=@squat_side.mp4
exerciseType=squat
cameraView=side
```

## 17.2. Validação no backend

Aceitar apenas:

```txt
front
side
```

Se vier vazio ou inválido, retornar 400:

```json
{
  "detail": "cameraView is required and must be either 'front' or 'side'."
}
```

## 17.3. Schema Python

Criar enum:

```python
from enum import Enum

class CameraView(str, Enum):
    FRONT = "front"
    SIDE = "side"
```

Adicionar ao input:

```python
camera_view: CameraView
```

## 17.4. Resposta da API

Exemplo:

```json
{
  "analysis_id": "uuid",
  "exercise_type": "squat",
  "camera_view": "side",
  "score": {
    "final_score": 81,
    "movement_quality_score": 79,
    "analysis_confidence": 91,
    "score_type": "AXON_LATERAL_MOVEMENT_SCORE",
    "score_version": "1.0.0",
    "classification": "Bom padrão, com pequenos ajustes",
    "summary": "Seu agachamento lateral apresenta boa profundidade e controle geral.",
    "components": [],
    "warnings": [],
    "recommendations": []
  }
}
```

---

# 18. Arquitetura backend sugerida

Estrutura sugerida:

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
        frontal_metrics.py
        lateral_metrics.py
      scoring/
        __init__.py
        engine.py
        schemas.py
        config.py
        components.py
        classification.py
        exercises/
          __init__.py
          squat_front.py
          squat_side.py
      feedback/
        generator.py
```

Adaptar ao padrão atual do projeto se os diretórios tiverem nomes diferentes.

---

# 19. Engine de score por exercício + câmera

Criar registry:

```python
SCORING_REGISTRY = {
    ("squat", "front"): calculate_squat_front_score,
    ("squat", "side"): calculate_squat_side_score,
}
```

Função:

```python
def calculate_score(scoring_input: ScoringInput) -> ScoreResult:
    key = (
        scoring_input.exercise_type.lower(),
        scoring_input.camera_view.value,
    )

    scoring_function = SCORING_REGISTRY.get(key)

    if not scoring_function:
        raise ValueError(f"Unsupported scoring configuration: {key}")

    return scoring_function(scoring_input)
```

---

# 20. Configuração de score

Criar ou ajustar:

```txt
backend/app/modules/scoring/config.py
```

Exemplo:

```python
SCORE_CONFIG = {
    ("squat", "front"): {
        "score_type": "AXON_FRONTAL_MOVEMENT_SCORE",
        "score_version": "1.0.0",
        "weights": {
            "symmetry": 0.25,
            "knee_alignment": 0.25,
            "frontal_stability": 0.20,
            "motor_control": 0.15,
            "analysis_confidence": 0.15,
        },
    },
    ("squat", "side"): {
        "score_type": "AXON_LATERAL_MOVEMENT_SCORE",
        "score_version": "1.0.0",
        "weights": {
            "amplitude_depth": 0.25,
            "joint_kinematics": 0.20,
            "trunk_posture": 0.20,
            "motor_control": 0.20,
            "analysis_confidence": 0.15,
        },
    },
}
```

---

# 21. Schemas de scoring

## 21.1. Input

```python
class ScoringInput(BaseModel):
    analysis_id: str
    exercise_type: str
    camera_view: CameraView
    metrics: dict
    reps: list[dict] | None = None
    pose_quality: dict | None = None
```

## 21.2. Output

```python
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
    score_type: str
    score_version: str
    classification: str
    summary: str
    components: list[ScoreComponent]
    warnings: list[str] = []
    recommendations: list[str] = []
```

---

# 22. Helpers de score

Criar ou reaproveitar:

```python
def clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))

def weighted_score(items: list[tuple[float, float]]) -> int:
    total_weight = sum(weight for _, weight in items)
    if total_weight <= 0:
        return 0

    value = sum(score * weight for score, weight in items) / total_weight
    return clamp_score(value)

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

# 23. Implementação do `squat_side.py`

Criar:

```txt
backend/app/modules/scoring/exercises/squat_side.py
```

Implementar:

```python
def calculate_squat_side_score(scoring_input: ScoringInput) -> ScoreResult:
    amplitude_depth = calculate_amplitude_depth_score(scoring_input.metrics)
    joint_kinematics = calculate_joint_kinematics_score(scoring_input.metrics)
    trunk_posture = calculate_trunk_posture_score(scoring_input.metrics)
    motor_control = calculate_lateral_motor_control_score(scoring_input.metrics)
    analysis_confidence = calculate_lateral_analysis_confidence_score(scoring_input.metrics)

    if analysis_confidence.score < 40:
        return build_lateral_inconclusive_result(...)

    movement_quality_score = weighted_score([
        (amplitude_depth.score, 0.25),
        (joint_kinematics.score, 0.20),
        (trunk_posture.score, 0.20),
        (motor_control.score, 0.20),
    ])

    final_score = weighted_score([
        (amplitude_depth.score, 0.25),
        (joint_kinematics.score, 0.20),
        (trunk_posture.score, 0.20),
        (motor_control.score, 0.20),
        (analysis_confidence.score, 0.15),
    ])

    return ScoreResult(...)
```

---

# 24. Métricas laterais

Criar:

```txt
backend/app/modules/biomechanics/lateral_metrics.py
```

Responsabilidades:

1. detectar lado mais visível;
2. extrair landmarks do lado visível;
3. calcular ângulo de joelho;
4. calcular ângulo de quadril;
5. calcular inclinação do tronco;
6. calcular profundidade;
7. calcular amplitude;
8. calcular ritmo;
9. calcular suavidade;
10. calcular confiança da análise lateral.

---

# 25. Detecção de repetições para lateral

Se já existir detecção de repetições, reaproveitar.

Para vídeo lateral, usar sinais como:

```txt
hip_y
knee_angle
hip_angle
```

Fluxo esperado:

```txt
topo
→ descida
→ ponto mais baixo
→ subida
→ retorno ao topo
```

Regras iniciais:

- identificar mínimos e máximos da altura do quadril;
- confirmar com variação do ângulo de joelho;
- remover ruído com smoothing;
- validar duração mínima da repetição;
- ignorar repetições incompletas.

---

# 26. Smoothing

Aplicar suavização nos sinais laterais:

- `knee_angle`;
- `hip_angle`;
- `trunk_inclination`;
- `hip_y`.

Sugestão inicial:

```txt
moving average
```

Objetivo:

- reduzir jitter;
- evitar penalizações frame a frame;
- melhorar detecção de repetição;
- aumentar estabilidade do score.

---

# 27. Frontend — alteração no upload

Adicionar seleção:

```txt
Tipo do vídeo

[ Frontal ] [ Lateral ]
```

Ou radio buttons:

```txt
( ) Frontal
( ) Lateral
```

## 27.1. Microcopy

Para frontal:

```txt
Use vídeo frontal para avaliar simetria, alinhamento dos joelhos e estabilidade lateral.
```

Para lateral:

```txt
Use vídeo lateral para avaliar profundidade, ângulo de joelho, quadril, tronco e controle do movimento.
```

## 27.2. Validação

O botão de análise deve ficar desabilitado se:

- não houver vídeo;
- não houver tipo de vídeo;
- não houver exercício, se o exercício for obrigatório.

## 27.3. Payload

```ts
formData.append("file", file);
formData.append("exerciseType", selectedExercise);
formData.append("cameraView", selectedCameraView);
```

---

# 28. Tipagem frontend

Criar ou ajustar:

```ts
export type CameraView = "front" | "side";

export type ScoreType =
  | "AXON_FRONTAL_MOVEMENT_SCORE"
  | "AXON_LATERAL_MOVEMENT_SCORE";

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
  score_type: ScoreType;
  score_version: string;
  classification: string;
  summary: string;
  components: ScoreComponent[];
  warnings: string[];
  recommendations: string[];
};
```

---

# 29. Dashboard

Na tela de resultado, exibir:

```txt
Tipo de análise: Lateral
Score: 81 / 100
Classificação: Bom padrão, com pequenos ajustes
```

Se `camera_view = side`, os cards devem ser:

- Amplitude e profundidade;
- Cinemática de joelho e quadril;
- Postura de tronco;
- Controle motor;
- Confiabilidade da análise.

Se `camera_view = front`, os cards devem ser os componentes frontais.

---

# 30. Aviso de limitação por ângulo

Se `camera_view = side`, exibir:

```txt
Esta análise lateral prioriza profundidade, ângulo de joelho, quadril, tronco e controle do movimento. Métricas de simetria frontal podem ser limitadas neste ângulo.
```

Se `camera_view = front`, exibir:

```txt
Esta análise frontal prioriza simetria, alinhamento dos joelhos e estabilidade lateral. Métricas de profundidade podem ser limitadas neste ângulo.
```

---

# 31. Exemplo de resposta lateral confiável

```json
{
  "analysis_id": "8b1f9f7b-8b1d-4d38-a1f3-1c2222222222",
  "exercise_type": "squat",
  "camera_view": "side",
  "score": {
    "final_score": 81,
    "movement_quality_score": 79,
    "analysis_confidence": 91,
    "score_type": "AXON_LATERAL_MOVEMENT_SCORE",
    "score_version": "1.0.0",
    "classification": "Bom padrão, com pequenos ajustes",
    "summary": "Seu agachamento lateral apresenta boa profundidade e controle geral, com leve inclinação de tronco no ponto mais baixo.",
    "components": [
      {
        "name": "amplitude_depth",
        "score": 84,
        "weight": 0.25,
        "status": "good",
        "details": [
          {
            "metric": "squat_depth",
            "value": 0.86,
            "status": "good",
            "message": "Boa profundidade no agachamento."
          }
        ]
      },
      {
        "name": "joint_kinematics",
        "score": 80,
        "weight": 0.2,
        "status": "good",
        "details": [
          {
            "metric": "knee_rom",
            "value": 88,
            "status": "good",
            "message": "Boa amplitude de joelho durante o movimento."
          }
        ]
      },
      {
        "name": "trunk_posture",
        "score": 72,
        "weight": 0.2,
        "status": "good",
        "details": [
          {
            "metric": "bottom_trunk_inclination",
            "value": 31,
            "status": "attention",
            "message": "O tronco inclinou um pouco no ponto mais baixo."
          }
        ]
      },
      {
        "name": "motor_control",
        "score": 78,
        "weight": 0.2,
        "status": "good",
        "details": [
          {
            "metric": "movement_smoothness",
            "value": 0.81,
            "status": "good",
            "message": "O movimento apresentou boa fluidez geral."
          }
        ]
      },
      {
        "name": "analysis_confidence",
        "score": 91,
        "weight": 0.15,
        "status": "reliable",
        "details": [
          {
            "metric": "valid_pose_frame_ratio",
            "value": 0.93,
            "status": "good",
            "message": "A maioria dos frames teve boa detecção corporal."
          }
        ]
      }
    ],
    "warnings": [],
    "recommendations": [
      "Tente manter o tronco um pouco mais estável no ponto mais baixo.",
      "Continue buscando controle na descida e na subida."
    ]
  }
}
```

---

# 32. Exemplo de resposta lateral inconclusiva

```json
{
  "analysis_id": "8b1f9f7b-8b1d-4d38-a1f3-1c2222222222",
  "exercise_type": "squat",
  "camera_view": "side",
  "score": {
    "final_score": null,
    "movement_quality_score": null,
    "analysis_confidence": 31,
    "score_type": "AXON_LATERAL_MOVEMENT_SCORE",
    "score_version": "1.0.0",
    "classification": "Análise inconclusiva",
    "summary": "Não foi possível gerar um score confiável para este vídeo lateral.",
    "components": [
      {
        "name": "analysis_confidence",
        "score": 31,
        "weight": 0.15,
        "status": "critical",
        "details": [
          {
            "metric": "critical_landmarks_visible_ratio",
            "value": 0.38,
            "status": "critical",
            "message": "Landmarks importantes como quadril, joelho ou tornozelo não ficaram visíveis o suficiente."
          }
        ]
      }
    ],
    "warnings": [
      "O corpo não ficou totalmente visível no vídeo lateral.",
      "A análise foi limitada pela baixa confiança dos landmarks."
    ],
    "recommendations": [
      "Grave novamente com o corpo inteiro visível de lado.",
      "Evite cortar pés, joelhos, quadril, tronco e cabeça.",
      "Mantenha a câmera parada durante todo o movimento.",
      "Use boa iluminação."
    ]
  }
}
```

---

# 33. Testes obrigatórios

Criar testes para:

```txt
detect_visible_side
calculate_amplitude_depth_score
calculate_joint_kinematics_score
calculate_trunk_posture_score
calculate_lateral_motor_control_score
calculate_lateral_analysis_confidence_score
calculate_squat_side_score
calculate_score com ("squat", "side")
calculate_score com ("squat", "front")
validação de cameraView inválido
```

---

# 34. Cenários de teste

## Cenário 1 — Vídeo lateral excelente

Input:

- boa profundidade;
- boa flexão de joelho;
- boa flexão de quadril;
- tronco controlado;
- boa confiança de pose.

Esperado:

- `final_score >= 85`;
- `score_type = AXON_LATERAL_MOVEMENT_SCORE`;
- classificação excelente;
- sem warnings críticos.

## Cenário 2 — Vídeo lateral com pouca profundidade

Input:

- quadril muito acima da linha do joelho;
- pouca flexão de joelho;
- boa confiança.

Esperado:

- `amplitude_depth < 70`;
- recomendação sobre profundidade/amplitude;
- score final penalizado.

## Cenário 3 — Vídeo lateral com tronco muito inclinado

Input:

- boa profundidade;
- tronco muito inclinado;
- boa confiança.

Esperado:

- `trunk_posture < 70`;
- recomendação sobre controle do tronco.

## Cenário 4 — Vídeo lateral com baixa confiança

Input:

- poucos landmarks visíveis;
- corpo cortado;
- baixa confiança.

Esperado:

- `final_score = null`;
- classificação = `Análise inconclusiva`;
- warnings explicativos.

## Cenário 5 — Vídeo frontal continua funcionando

Input:

```txt
cameraView = front
```

Esperado:

- engine chama score frontal;
- não chama score lateral;
- payload retorna `camera_view = front`.

## Cenário 6 — cameraView inválido

Input:

```txt
cameraView = diagonal
```

Esperado:

- erro 400;
- mensagem clara.

---

# 35. Critérios de aceite funcionais

A implementação estará concluída quando:

1. O usuário conseguir selecionar `Frontal` ou `Lateral` no upload.
2. O frontend enviar `cameraView` para o backend.
3. O backend validar `cameraView`.
4. O engine de score usar `exerciseType + cameraView`.
5. O score lateral for calculado por regras específicas.
6. O score frontal atual continuar funcionando.
7. O dashboard exibir o tipo de análise.
8. O dashboard exibir componentes diferentes para análise lateral.
9. Vídeos laterais com baixa confiança não retornarem score falso.
10. A resposta da API indicar `score_type` e `score_version`.

---

# 36. Critérios técnicos

1. Não calcular score no frontend.
2. Não aplicar regra frontal em vídeo lateral.
3. Não aplicar regra lateral em vídeo frontal.
4. Não usar score 0 para análise inconclusiva.
5. Centralizar pesos em config.
6. Criar registry por exercício e tipo de câmera.
7. Criar testes unitários.
8. Manter tipagem clara.
9. Manter compatibilidade com fluxo existente.
10. Evitar linguagem médica no feedback.

---

# 37. Roadmap de implementação

## Fase 1 — Frontend: seleção do tipo de vídeo

Entregáveis:

- radio/select `Frontal` e `Lateral`;
- campo obrigatório;
- envio no `FormData`;
- tipagem `CameraView`.

## Fase 2 — Backend: receber e validar `cameraView`

Entregáveis:

- enum `CameraView`;
- validação no endpoint;
- propagação no pipeline;
- retorno de `camera_view`.

## Fase 3 — Engine por câmera

Entregáveis:

- registry `("squat", "front")`;
- registry `("squat", "side")`;
- ajuste no `calculate_score`;
- testes de roteamento.

## Fase 4 — Métricas laterais

Entregáveis:

- `lateral_metrics.py`;
- detecção de lado visível;
- cálculo de joelho, quadril, tronco;
- cálculo de profundidade;
- métricas de controle temporal.

## Fase 5 — Score lateral

Entregáveis:

- `squat_side.py`;
- componentes do score lateral;
- feedback específico;
- tratamento de análise inconclusiva.

## Fase 6 — Dashboard

Entregáveis:

- label de tipo de análise;
- cards específicos para lateral;
- alerta sobre limitações do ângulo;
- recomendações específicas.

## Fase 7 — Testes e calibração

Entregáveis:

- testes unitários;
- testes de contrato;
- testes manuais com vídeos laterais reais;
- ajustes iniciais de thresholds.

---

# 38. Backlog direto para o Codex

## Tarefa 1 — Frontend: adicionar seleção no upload

Adicionar na tela de upload:

```txt
Tipo do vídeo:
- Frontal
- Lateral
```

Regras:

- campo obrigatório;
- valor salvo em estado;
- enviado no upload;
- botão de análise desabilitado sem seleção.

## Tarefa 2 — Frontend: enviar `cameraView`

Atualizar:

```ts
formData.append("cameraView", selectedCameraView);
```

Garantir tipo:

```ts
type CameraView = "front" | "side";
```

## Tarefa 3 — Backend: criar enum

```python
class CameraView(str, Enum):
    FRONT = "front"
    SIDE = "side"
```

## Tarefa 4 — Backend: validar no endpoint

Se ausente ou inválido, retornar 400.

## Tarefa 5 — Backend: propagar no pipeline

Garantir passagem:

```txt
route
→ service
→ video processing
→ metrics extraction
→ scoring engine
```

## Tarefa 6 — Backend: registry

```python
SCORING_REGISTRY = {
    ("squat", "front"): calculate_squat_front_score,
    ("squat", "side"): calculate_squat_side_score,
}
```

## Tarefa 7 — Backend: criar score lateral

Criar:

```txt
backend/app/modules/scoring/exercises/squat_side.py
```

Implementar:

- `calculate_squat_side_score`;
- `calculate_amplitude_depth_score`;
- `calculate_joint_kinematics_score`;
- `calculate_trunk_posture_score`;
- `calculate_lateral_motor_control_score`;
- `calculate_lateral_analysis_confidence_score`.

## Tarefa 8 — Backend: criar métricas laterais

Criar:

```txt
backend/app/modules/biomechanics/lateral_metrics.py
```

Implementar:

- `detect_visible_side`;
- cálculo de ângulo de joelho;
- cálculo de ângulo de quadril;
- cálculo de inclinação de tronco;
- cálculo de profundidade;
- cálculo de ritmo;
- cálculo de confiança lateral.

## Tarefa 9 — Frontend: ajustar dashboard

Se `camera_view = side`, exibir cards:

- Amplitude e profundidade;
- Cinemática de joelho e quadril;
- Postura de tronco;
- Controle motor;
- Confiabilidade.

Se `camera_view = front`, exibir cards frontais.

## Tarefa 10 — Testes

Criar testes para:

- seleção obrigatória;
- payload com `cameraView`;
- validação backend;
- roteamento do score;
- cálculo do score lateral;
- análise inconclusiva;
- compatibilidade frontal.

---

# 39. Prompt direto para o Codex

Implementar suporte a análise de vídeos lateralizados na AXON.

Hoje o projeto já analisa vídeos e calcula score, mas as métricas atuais foram pensadas principalmente para vídeos frontais.

Precisamos adicionar no upload uma seleção obrigatória do tipo de vídeo:

- Frontal;
- Lateral.

Essa seleção deve ser enviada ao backend como:

```ts
cameraView: "front" | "side"
```

No backend, criar roteamento de score por combinação de exercício e tipo de câmera:

```python
("squat", "front")
("squat", "side")
```

Criar um novo score para vídeos laterais chamado:

```txt
AXON_LATERAL_MOVEMENT_SCORE
```

O score lateral deve ter os seguintes componentes:

- `amplitude_depth` com peso 25%;
- `joint_kinematics` com peso 20%;
- `trunk_posture` com peso 20%;
- `motor_control` com peso 20%;
- `analysis_confidence` com peso 15%.

O foco inicial é o exercício `squat`.

Não quebrar o score frontal atual.

Não aplicar métricas frontais em vídeos laterais.

Não aplicar métricas laterais em vídeos frontais.

Não retornar score 0 quando a análise for inconclusiva. Usar `final_score = null`.

Atualizar o dashboard para exibir o tipo de análise e os componentes corretos do score.

Criar testes unitários para o novo fluxo.

---

# 40. Evolução futura

No futuro, a AXON pode ter três modos:

```txt
Análise frontal
Análise lateral
Análise completa
```

A análise completa poderá aceitar dois vídeos:

```txt
1 vídeo frontal
1 vídeo lateral
```

E retornar:

```json
{
  "front_score": 76,
  "side_score": 83,
  "final_score": 80
}
```

Mas isso não deve ser implementado agora.

O foco desta implementação é:

```txt
1 vídeo
1 tipo de câmera
1 score coerente com o ângulo selecionado
```

---

# 41. Checklist final

- [ ] Adicionar seleção Frontal/Lateral no upload.
- [ ] Criar tipo `CameraView`.
- [ ] Enviar `cameraView` no upload.
- [ ] Validar `cameraView` no backend.
- [ ] Propagar `cameraView` no pipeline.
- [ ] Criar registry de score por `exerciseType + cameraView`.
- [ ] Manter score frontal funcionando.
- [ ] Criar `AXON_LATERAL_MOVEMENT_SCORE`.
- [ ] Criar componentes laterais.
- [ ] Criar métricas laterais.
- [ ] Detectar lado visível automaticamente.
- [ ] Tratar baixa confiança.
- [ ] Usar `final_score = null` para análise inconclusiva.
- [ ] Atualizar dashboard.
- [ ] Exibir tipo de análise.
- [ ] Exibir cards laterais.
- [ ] Criar testes unitários.
- [ ] Criar testes de contrato.
- [ ] Documentar limitações de cada ângulo.
