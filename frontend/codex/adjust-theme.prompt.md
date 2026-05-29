# tesla-ui-theme-update.prompt.md — Atualização do Tema Visual para Tesla UI Feeling

## Objetivo

Atualizar o frontend da plataforma Sport AI para um visual muito mais próximo da identidade visual da Tesla.

O visual atual está muito próximo de:

```txt
dark SaaS dashboard
```

Mas o objetivo correto é:

```txt
Tesla App + Tesla Website + Performance Technology
```

---

# Nova direção visual

A interface deve transmitir:

- minimalismo
- tecnologia premium
- precisão
- sofisticação
- clareza
- sensação automotiva
- performance
- clean UI

O frontend NÃO deve parecer:

- app gamer
- dashboard corporativo pesado
- fintech escura
- academia genérica
- cyberpunk
- neon futurista

---

# Referências visuais

Usar como referência:

- Tesla Website
- Tesla Mobile App
- Apple Fitness
- Whoop
- Oura

Mas a principal referência deve ser:

```txt
Tesla UI Feeling
```

---

# Nova paleta obrigatória

## Background principal

```txt
#F4F4F4
```

---

## Surface / Cards

```txt
#FFFFFF
```

---

## Surface Secondary

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

Tesla Red:

```txt
#E82127
```

---

## Dark section opcional

```txt
#171A20
```

---

# Estilo visual obrigatório

## Layout

A interface deve usar:

- muito espaço em branco
- alinhamento limpo
- grids organizados
- cards grandes
- foco visual no conteúdo
- poucos elementos simultâneos
- muito respiro visual

---

## Tipografia

A tipografia deve parecer:

```txt
forte
premium
minimalista
automotiva
```

Usar:

- font-semibold
- tracking leve
- títulos grandes
- subtítulos limpos
- evitar textos excessivos

---

# Cards

Todos os cards devem:

- possuir fundo branco
- possuir borda cinza clara
- radius grande
- sombra extremamente sutil
- aparência premium
- layout limpo

---

# NÃO usar

Evitar:

- glow
- neon
- gradientes exagerados
- bordas coloridas
- glassmorphism exagerado
- efeitos gamer
- sombras fortes
- excesso de blur

---

# Botões

## Primary Button

Visual:

```txt
background: #171A20
text: branco
hover: preto puro
```

Exemplo de CTA:

```txt
Analisar treino
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
text: #171A20
border: #D0D1D2
```

---

# Hero Section

## Objetivo

A Hero Section deve parecer:

```txt
produto premium de tecnologia
```

E NÃO:

```txt
landing page fitness genérica
```

---

# Hero Layout

## Lado esquerdo

Texto:

```txt
Transforme seus vídeos de treino em métricas biomecânicas inteligentes.
```

Subtexto:

```txt
Envie seu treino, acompanhe sua execução e receba insights biomecânicos com IA.
```

Botões:

- Analisar treino
- Ver demonstração

---

## Lado direito

Criar um painel premium contendo:

- overall score
- total reps
- stability score
- feedback curto
- movimento: Back Squat

Esse painel deve parecer:

```txt
painel automotivo premium
```

---

# Navbar

Navbar extremamente minimalista.

## Deve conter

- logo
- Features
- How it Works
- Upload
- botão CTA

---

# Results Dashboard

## Objetivo

A tela de resultado deve parecer:

```txt
painel premium de performance esportiva
```

---

# Score principal

O Overall Score deve ser:

- muito grande
- central
- elegante
- minimalista

Exemplo:

```txt
84/100
```

---

# Cards do dashboard

Os cards devem possuir:

- muito espaçamento
- poucas informações
- foco no dado principal
- visual clean

---

# Gráficos

Os gráficos devem:

- usar poucas cores
- visual limpo
- linhas suaves
- sem grid exagerado
- sem excesso de elementos

---

# Performance Charts

Usar:

- Recharts

Criar gráficos para:

- knee angle over time
- stability per rep
- score breakdown

---

# Animações

Usar:

- Framer Motion

Mas com extrema moderação.

Objetivo:

```txt
microinterações suaves
```

Evitar:

- animações chamativas
- bounce exagerado
- zoom exagerado

---

# Estrutura visual recomendada

## Espaçamento

Usar:

```txt
p-6
p-8
gap-6
gap-8
rounded-2xl
```

---

# Shadows

Usar apenas:

```txt
shadow-sm
```

ou:

```txt
shadow-[0_2px_10px_rgba(0,0,0,0.04)]
```

---

# Responsividade

A interface deve funcionar muito bem em:

- desktop
- notebook
- tablet

Mobile pode ser simples inicialmente.

---

# Componentes que devem ser atualizados

Atualizar:

```txt
Header
HeroSection
FeatureCards
VideoUploadCard
ScoreSummary
FeedbackPanel
MetricsCards
PerformanceCharts
```

---

# Tailwind

Atualizar classes Tailwind para refletir o novo visual Tesla.

---

# Resultado esperado

O frontend final deve parecer:

```txt
Tesla App analisando performance esportiva.
```

E transmitir:

```txt
tecnologia
precisão
performance
premium
minimalismo
```

---

# Critérios de aceite

A implementação estará pronta quando:

- visual estiver claro/minimalista
- aparência lembrar Tesla UI
- cards estiverem clean
- tipografia estiver premium
- dashboard estiver elegante
- upload estiver bonito
- overall score estiver destacado
- experiência estiver fluida
- UI não parecer gamer
- UI não parecer dashboard corporativo pesado
- experiência geral parecer produto premium
