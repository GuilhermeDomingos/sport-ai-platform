# Sport AI Platform

Plataforma de analise esportiva por video com IA, organizada como monorepo
para evoluir a interface web e o processamento de videos separadamente.

## Estrutura

```txt
sport-ai-platform/
  frontend/                 # Aplicacao Next.js 16 com App Router
    public/
    src/
      app/                  # Home Athlete Vision AI e layout raiz
      components/           # Componentes interativos, incluindo VideoUpload
    eslint.config.mjs
    next.config.ts
    package.json
    postcss.config.mjs
    tsconfig.json
  backend/                  # API FastAPI para upload local de videos
    app/                    # Rotas, schemas, servicos e uploads
    requirements.txt
    README.md
  package.json              # Workspaces e scripts de orquestracao
  package-lock.json         # Lockfile compartilhado
```

O frontend possui a landing page Athlete Vision AI e um upload local com
pre-visualizacao. No upload, o usuario seleciona se o video e frontal ou
lateral; essa escolha e enviada ao backend como `cameraView` e roteia as
metricas e o score corretos para o angulo da camera.
O backend fornece uma API inicial para receber, validar, armazenar e consultar
videos, alem de extrair metadados tecnicos reais com OpenCV.
O backend tambem extrai frames locais e detecta landmarks corporais com
MediaPipe, calculando metricas biomecanicas iniciais do squat em 2D e
segmentando repeticoes ao longo do movimento para gerar score frontal ou
lateral (`AXON_FRONTAL_MOVEMENT_SCORE` ou `AXON_LATERAL_MOVEMENT_SCORE`),
feedbacks e um relatorio real consolidado em
`GET /videos/{video_id}/analysis`.

## Stack atual

- Frontend: Next.js 16.2.6, React 19, TypeScript e Tailwind CSS 4.
- Monorepo: npm workspaces.
- Backend: Python 3.11, FastAPI, Uvicorn, OpenCV, MediaPipe, armazenamento
  local de videos, extracao de frames, deteccao de pose, metricas de squat,
  analise temporal de repeticoes, AXON Movement Score por angulo de camera e
  feedback deterministico.

Antes de alterar APIs ou convencoes do Next.js, consulte a documentacao local
instalada em `node_modules/next/dist/docs/`, conforme `AGENTS.md`.

## Execucao

Na raiz, instale as dependencias:

```bash
npm install
```

Execute o frontend:

```bash
npm run dev
```

O comando permanece disponivel na raiz e encaminha para o workspace
`@sport-ai-platform/frontend`. A aplicacao abre normalmente em
`http://localhost:3000`.

## Scripts da raiz

```bash
npm run dev
npm run dev:frontend
npm run build
npm run build:frontend
npm run start
npm run lint
```

Atualmente esses scripts npm executam o frontend. O backend e executado a
partir de `backend/` com `python -m uvicorn app.main:app --reload --port 8000`;
consulte `backend/README.md` para instalacao e endpoints.

## Proximas decisoes do backend

- Definir estrategia de armazenamento persistente alem do ambiente local.
- Modelar o processamento assincrono e as metricas geradas por IA.
- Documentar variaveis de ambiente em `backend/.env.example`.
