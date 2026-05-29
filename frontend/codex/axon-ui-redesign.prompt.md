
# axon-ui-redesign.prompt.md — Redesign Completo da UI da AXON

## Contexto

A plataforma mudou oficialmente para:

```txt
AXON
```

A nova identidade visual deve seguir uma direção:

```txt
Tesla UI Feeling
```

O objetivo é transmitir:

- precisão
- performance
- tecnologia premium
- biomecânica
- minimalismo
- engenharia
- inteligência

---

# Filosofia visual

A AXON deve parecer:

```txt
Tesla analisando performance humana.
```

A aplicação NÃO deve parecer:

- dashboard SaaS genérico
- app gamer
- visual neon
- app fitness comum
- fintech escura

---

# Paleta oficial da AXON

## Background principal

```txt
#F3F4F6
```

---

## Cards / Surface

```txt
#FFFFFF
```

---

## Surface secondary

```txt
#F8F8F8
```

---

## Texto principal

```txt
#171A20
```

---

## Texto secundário

```txt
#5C5E62
```

---

## Borders

```txt
#D0D1D2
```

---

## Accent principal

Usar SOMENTE:

```txt
#E82127
```

Esse vermelho deve ser usado apenas em:

- CTA principal
- pequenos destaques
- loading ativo
- status importantes

---

# Typography

## Fonte obrigatória

Usar:

```txt
Inter
```

---

# Direção tipográfica

A tipografia deve parecer:

```txt
engenharia premium
```

Usar:

- títulos grandes
- muito espaço
- hierarquia limpa
- poucas linhas
- tracking leve
- font-semibold

---

# Layout Philosophy

A interface deve usar:

- muito espaço em branco
- grids organizados
- alinhamento limpo
- poucos elementos simultâneos
- foco visual forte

---

# Cards

Todos os cards devem:

- possuir fundo branco
- possuir borda cinza muito sutil
- radius grande
- sombra extremamente leve

---

# Tailwind padrão

Usar:

```txt
bg-white
border border-zinc-200
rounded-3xl
shadow-sm
```

---

# NÃO usar

Evitar:

- glow
- neon
- glassmorphism exagerado
- gradients fortes
- sombras fortes
- visual gamer

---

# Botões

## Primary Button

Visual:

```txt
background: #171A20
text: branco
```

---

## Accent Button

Visual:

```txt
background: #E82127
text: branco
```

---

## Secondary Button

Visual:

```txt
background: transparente
border: #D0D1D2
text: #171A20
```

---

# Navbar

A navbar deve ser extremamente minimalista.

## Deve conter

- logo AXON
- Features
- How it Works
- Upload
- CTA principal

---

# Hero Section

## Headline

```txt
Human Performance.
Measured Precisely.
```

---

## Subheadline

```txt
Upload your training video and receive biomechanical analysis, rep detection and intelligent performance insights.
```

---

# Hero visual

Criar painel premium contendo:

- AXON Analysis Ready
- Overall Score
- Total Reps
- Stability Score
- Feedback curto

Esse painel deve parecer:

```txt
painel automotivo premium
```

---

# Dashboard

A dashboard deve parecer:

```txt
painel premium de performance humana
```

---

# Performance Score

O score deve ser:

- gigante
- minimalista
- elegante
- central

Exemplo:

```txt
84
Performance Score
```

---

# Upload Experience

O upload deve parecer:

```txt
software premium de tecnologia
```

---

# Processing Experience

Mostrar etapas:

```txt
Uploading
Processing Video
Extracting Frames
Detecting Pose
Calculating Metrics
Analyzing Movement
Calculating Score
Generating Feedback
```

---

# Motion Design

Usar:

```txt
Framer Motion
```

Mas apenas para:

- fade
- microinterações
- smooth transitions

---

# NÃO usar

Evitar:

- bounce exagerado
- zoom exagerado
- animações chamativas

---

# Charts

Usar:

```txt
Recharts
```

Criar:

- Knee Angle Over Time
- Stability Per Rep
- Score Breakdown

---

# Regras dos gráficos

- poucas cores
- linhas suaves
- muito espaço em branco
- sem visual corporativo pesado

---

# Componentes que devem ser atualizados

Atualizar:

```txt
Header
HeroSection
FeatureCards
VideoUploadCard
ProcessingSteps
ScoreSummary
FeedbackPanel
MetricsCards
RepBreakdownTable
PerformanceCharts
Buttons
Cards
Badges
```

---

# Design System AXON

Criar componentes:

```txt
Button
Card
Badge
SectionTitle
MetricCard
ScoreDisplay
StatusPill
```

---

# Resultado esperado

A aplicação final deve transmitir:

```txt
tecnologia
performance
engenharia
precisão
minimalismo
premium
```

O usuário deve sentir:

```txt
“Isso parece tecnologia de elite.”
```
