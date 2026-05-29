# frontend-mvp-tesla-ui.prompt.md — Plano de Implementação do Frontend MVP

## Contexto do projeto

Estou criando uma plataforma web chamada inicialmente **Sport AI Platform**.

A plataforma será voltada para análise esportiva por vídeo com IA, começando por:

- Esporte: Crossfit
- Movimento inicial: Back Squat

O backend já possui o pipeline completo:

```txt
Upload
→ Processing
→ Frame Extraction
→ Pose Detection
→ Biomechanics
→ Movement Analysis
→ Scoring
→ Feedback
```

Agora quero iniciar o frontend MVP.

---

# Objetivo do Frontend MVP

Criar uma experiência mínima, premium e funcional onde o usuário consiga:

1. acessar uma landing/home
2. fazer upload de um vídeo de treino
3. acompanhar o processamento
4. visualizar o resultado da análise
5. entender score, reps e feedback
6. perceber valor imediatamente

---

# Direção visual

## Tema principal

```txt
Tesla UI feeling
```

A interface deve transmitir:

- tecnologia
- performance
- precisão
- minimalismo
- premium
- controle
- inteligência

---

# Diretrizes visuais

## Aparência

Usar uma estética:

```txt
dark premium
minimalista
high-tech
automotiva
limpa
```

## Cores

Evitar preto puro absoluto como fundo principal.

Usar:

```txt
background principal: #0B0F14
cards: #111827 ou #151A21
borders: rgba(255,255,255,0.08)
text principal: #F4F4F5
text secundário: #A1A1AA
accent: #E5E7EB ou azul/ciano discreto
success: verde discreto
warning: amarelo/laranja discreto
danger: vermelho discreto
```

## Estilo

- cards com bordas arredondadas
- glass effect sutil
- sombras suaves
- muita área de respiro
- tipografia forte
- hierarquia clara
- animações discretas
- não usar visual colorido demais
- não poluir a interface

---

# Stack obrigatória

- Next.js
- TypeScript
- Tailwind CSS
- App Router

---

# Bibliotecas permitidas

Pode usar:

```txt
lucide-react
framer-motion
recharts
```

Se ainda não estiverem instaladas, instalar:

```bash
npm install lucide-react framer-motion recharts
```

---

# Não implementar agora

Não implementar:

- login
- cadastro
- banco de dados
- pagamento
- área do atleta completa
- múltiplos esportes
- histórico real
- autenticação
- integração com storage cloud
- mobile app nativo

---

# Estrutura esperada do frontend

Criar ou organizar a estrutura:

```txt
src/
├── app/
│   ├── page.tsx
│   └── results/
│       └── [videoId]/
│           └── page.tsx
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   ├── home/
│   │   ├── HeroSection.tsx
│   │   ├── HowItWorks.tsx
│   │   ├── FeatureCards.tsx
│   │   └── DemoPreview.tsx
│   ├── upload/
│   │   ├── VideoUploadCard.tsx
│   │   └── ProcessingSteps.tsx
│   ├── results/
│   │   ├── ScoreSummary.tsx
│   │   ├── FeedbackPanel.tsx
│   │   ├── RepBreakdownTable.tsx
│   │   ├── MetricsCards.tsx
│   │   └── PerformanceCharts.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Card.tsx
│       └── Badge.tsx
├── services/
│   └── sportAiApi.ts
├── types/
│   └── analysis.ts
└── lib/
    └── formatters.ts
```

---

# Fase 1 — Criar Home/Landing Page

## Arquivo

```txt
src/app/page.tsx
```

## Objetivo

Criar uma landing page premium para explicar o produto e permitir upload do vídeo.

---

## Seções obrigatórias

### 1. Header

Deve conter:

- nome/logo da plataforma
- links:
  - Como funciona
  - Métricas
  - Upload
- botão CTA:
  - Analisar treino

---

### 2. Hero Section

Deve conter:

Título:

```txt
Transforme seus vídeos de treino em métricas biomecânicas inteligentes.
```

Subtítulo:

```txt
Envie seu vídeo de Crossfit, acompanhe sua execução e receba score, reps e feedback técnico com apoio de IA.
```

Botões:

```txt
Analisar meu treino
Ver demonstração
```

Visual lateral:

- card com score fake
- movimento: Back Squat
- status: Analysis Ready
- overall score: 84/100
- total reps: 8
- feedback curto

---

### 3. Como funciona

Mostrar 4 passos:

```txt
1. Envie seu vídeo
2. A IA detecta sua pose
3. O sistema calcula métricas biomecânicas
4. Você recebe score e feedback
```

---

### 4. Benefícios

Cards:

- Análise por repetição
- Score biomecânico
- Feedback acionável
- Evolução técnica
- Detecção de fadiga
- Visão de performance

---

### 5. Upload Section

Incluir componente:

```txt
VideoUploadCard
```

O usuário deve conseguir selecionar um vídeo.

---

# Fase 2 — Criar serviço de integração com API

## Arquivo

```txt
src/services/sportAiApi.ts
```

Criar funções para consumir backend:

```ts
const API_BASE_URL = "http://localhost:8000";

export async function uploadVideo(file: File) {}

export async function processVideo(videoId: string) {}

export async function extractFrames(videoId: string) {}

export async function detectPose(videoId: string) {}

export async function calculateMetrics(videoId: string) {}

export async function analyzeMovement(videoId: string) {}

export async function calculateScore(videoId: string) {}

export async function generateFeedback(videoId: string) {}
```

---

# Fase 3 — Criar fluxo completo de upload + processamento

## Componente

```txt
src/components/upload/VideoUploadCard.tsx
```

## Comportamento esperado

O usuário seleciona um vídeo.

Ao clicar em:

```txt
Analisar vídeo
```

O frontend deve executar em sequência:

```txt
1. uploadVideo
2. processVideo
3. extractFrames
4. detectPose
5. calculateMetrics
6. analyzeMovement
7. calculateScore
8. generateFeedback
```

---

## Estados obrigatórios

Criar estados:

```txt
idle
uploading
processing
extracting_frames
detecting_pose
calculating_metrics
analyzing_movement
calculating_score
generating_feedback
completed
error
```

---

## UI de processamento

Mostrar etapas:

```txt
Upload concluído
Processando vídeo
Extraindo frames
Detectando pose
Calculando métricas
Analisando reps
Calculando score
Gerando feedback
```

Cada etapa deve ter:

- ícone
- label
- status visual
- loading quando em execução
- check quando concluído

---

## Ao finalizar

Redirecionar para:

```txt
/results/{videoId}
```

ou renderizar resultado na própria tela se a rota ainda não estiver criada.

---

# Fase 4 — Criar página de resultado

## Arquivo

```txt
src/app/results/[videoId]/page.tsx
```

## Objetivo

Exibir o resultado da análise do treino.

Como o backend ainda pode não possuir endpoints GET para todos os arquivos, nesta fase pode:

- usar o retorno final do fluxo em memória
- ou criar um mock local temporário
- ou consumir o retorno do endpoint de feedback

---

# Seções da Results Page

## 1. Score Summary

Componente:

```txt
ScoreSummary.tsx
```

Deve mostrar:

- overall score grande
- movimento: Back Squat
- status: Analysis Complete
- total reps
- classificação:
  - Excellent
  - Good
  - Needs Attention

---

## 2. Feedback Panel

Componente:

```txt
FeedbackPanel.tsx
```

Mostrar:

- summary
- strengths
- improvements
- recommendations

---

## 3. Rep Breakdown

Componente:

```txt
RepBreakdownTable.tsx
```

Tabela:

```txt
Rep | Depth | Stability | Min Knee Angle | Duration
```

---

## 4. Metrics Cards

Componente:

```txt
MetricsCards.tsx
```

Cards:

- Average Knee Angle
- Min Knee Angle
- Depth Classification
- Stability Score
- Symmetry Score
- Consistency Score

---

## 5. Performance Charts

Componente:

```txt
PerformanceCharts.tsx
```

Usar Recharts para criar:

- stability per rep
- knee angle per rep
- score breakdown

---

# Fase 5 — Tipos TypeScript

## Arquivo

```txt
src/types/analysis.ts
```

Criar types:

```ts
export type UploadResponse = {
  message: string;
  videoId: string;
  filename: string;
  originalFilename: string;
  contentType: string;
  size: number;
  path: string;
};

export type ScoreResponse = {
  videoId: string;
  status: string;
  movement: string;
  score: {
    overallScore: number;
    depthScore: number;
    stabilityScore: number;
    symmetryScore: number;
    consistencyScore: number;
  };
};

export type FeedbackResponse = {
  videoId: string;
  status: string;
  movement: string;
  summary: string;
  strengths: string[];
  improvements: string[];
  recommendations: string[];
};

export type RepAnalysis = {
  rep: number;
  startFrame: number;
  bottomFrame: number;
  endFrame: number;
  depth: string;
  minKneeAngle: number;
  stabilityScore: number;
  durationFrames: number;
  averageVelocity: number;
};
```

---

# Fase 6 — Design System simples

Criar componentes base:

```txt
Button
Card
Badge
```

## Button

Variações:

```txt
primary
secondary
ghost
```

## Card

Deve ter:

```txt
rounded-2xl
border
bg-white/5
backdrop-blur
shadow
```

## Badge

Para status:

```txt
completed
processing
warning
error
```

---

# Critérios de aceite

A implementação estará pronta quando:

- app rodar com `npm run dev`
- home carregar sem erro
- visual dark premium estiver aplicado
- upload de vídeo funcionar
- frontend chamar o backend em sequência
- estados de processamento aparecerem
- resultado final ser exibido
- página de resultado existir
- score ser exibido com destaque
- feedback ser exibido de forma clara
- UI estiver responsiva
- não houver implementação de login
- não houver dependência de banco de dados

---

# Resultado esperado do MVP

O usuário deve conseguir:

```txt
Abrir a plataforma
→ entender a proposta
→ enviar vídeo
→ acompanhar processamento
→ receber score
→ visualizar feedback
```

---

# Observações finais

## Prioridade máxima

A prioridade é:

```txt
percepção de valor
```

O usuário precisa sentir que está usando uma ferramenta premium de análise esportiva.

## Visual

A interface deve parecer:

```txt
Tesla UI feeling + fitness analytics + biomecânica
```

## Evitar

Evitar:

- excesso de texto
- excesso de cores
- visual infantil
- dashboards poluídos
- experiência muito técnica
- termos científicos sem explicação

## Linguagem do produto

Trocar linguagem técnica por linguagem de performance.

Exemplo:

Evitar:

```txt
Ângulo médio do joelho: 92.4
```

Preferir:

```txt
Boa profundidade, com leve perda de estabilidade nas últimas reps.
```
